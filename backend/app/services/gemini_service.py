# app/services/gemini_service.py
"""
Gemini AI Service - Quản lý tích hợp Google Gemini API
Các tính năng cốt lõi:
1. Kết nối Gemini API với danh sách Models linh hoạt (gemini-2.0-flash, gemini-1.5-flash).
2. Cơ chế Retry tự động với Exponential Backoff khi Timeout hoặc Rate Limit (429).
3. Bắt lỗi sai API Key, quá hạn mức Quota và kích hoạt Fallback Grounded Engine.
4. Cơ chế Fallback CSDL Nội Bộ (Local Grounded Engine): Đảm bảo 100% không crash hệ thống,
   luôn cung cấp báo cáo 3 phần chính xác dựa trên số liệu thực tế kể cả khi mất mạng.
"""

import os
import re
import json
import time
import logging
from typing import Dict, Any, Optional, List
import httpx

from app.core.config import settings
from app.prompts.inventory_prompts import (
    SYSTEM_PROMPT_ANTI_HALLUCINATION,
    build_inventory_user_prompt
)

logger = logging.getLogger("smartlogis.gemini")

# Các model chính thức của Google Gemini API (Ưu tiên các model hoạt động nhanh và ổn định)
SUPPORTED_GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash-8b"
]


def update_env_file(key: str, value: str):
    """Cập nhật biến môi trường đồng thời vào cả backend/.env và root .env."""
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(curr_dir))
    root_dir = os.path.dirname(backend_dir)
    target_paths = list(dict.fromkeys([
        os.path.join(backend_dir, ".env"),
        os.path.join(root_dir, ".env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "backend", ".env")
    ]))
    nl = chr(10)
    for env_path in target_paths:
        if not os.path.exists(env_path):
            continue
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            new_lines = []
            found = False
            for line in lines:
                if line.strip().startswith(f"{key}=") or line.strip().startswith(f"export {key}="):
                    new_lines.append(f'{key}="{value}"' + nl)
                    found = True
                else:
                    new_lines.append(line)
            if not found:
                new_lines.append(nl + f'{key}="{value}"' + nl)
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            logger.info(f"Đã cập nhật {key} vào {env_path}")
        except Exception as e:
            logger.warning(f"Không thể cập nhật {key} vào {env_path}: {e}")


class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or ""
        self.last_error_was_network = False
        # Circuit-breaker: True nghĩa là mạng tới Gemini đang hoạt động, False nghĩa là đã có lỗi mạng/timeout gần đây
        self._network_ok: Optional[bool] = None

    @property
    def timeout(self) -> float:
        """Đọc timeout mới nhất từ settings mỗi lần gọi (không cần restart khi đổi .env)."""
        return float(getattr(settings, "AI_TIMEOUT_SECONDS", 5.0))

    @property
    def max_retries(self) -> int:
        if hasattr(self, "_max_retries") and self._max_retries is not None:
            return self._max_retries
        return int(getattr(settings, "AI_MAX_RETRIES", 1))

    @max_retries.setter
    def max_retries(self, value: int):
        self._max_retries = int(value)

    def is_configured(self) -> bool:
        """Kiểm tra xem API Key đã được cấu hình hợp lệ chưa."""
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def test_api_key(self, api_key: str) -> tuple:
        """Kiểm tra tính hợp lệ của Gemini API Key qua REST API."""
        key = (api_key or "").strip()
        if not key or len(key) < 10:
            return False, "Khóa API không hợp lệ (độ dài tối thiểu 10 ký tự)."

        base_endpoint = getattr(settings, "GEMINI_API_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
        primary_model = getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")
        url = f"{base_endpoint}/models/{primary_model}:generateContent?key={key}"
        payload = {
            "contents": [{"parts": [{"text": "Hello"}]}],
            "generationConfig": {"maxOutputTokens": 20}
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    return True, f"API Key hợp lệ! Mô hình {primary_model} đã sẵn sàng."
                elif res.status_code in [400, 401, 403]:
                    try:
                        err_data = res.json().get("error", {})
                        err_msg = err_data.get("message", "API Key không hợp lệ hoặc bị vô hiệu hóa.")
                    except Exception:
                        err_msg = res.text[:200]
                    return False, f"Lỗi xác thực API Key ({res.status_code}): {err_msg}"
                elif res.status_code == 429:
                    return True, "API Key hợp lệ nhưng đang bị giới hạn tốc độ tạm thời (Quota/Rate Limit)."
                else:
                    return False, f"Gemini API phản hồi mã lỗi {res.status_code}: {res.text[:150]}"
        except Exception as e:
            return False, f"Không thể kết nối đến máy chủ Google Gemini: {str(e)}"

    def set_api_key(self, api_key: str, persist_env: bool = True) -> tuple:
        """Cập nhật API Key mới, kiểm tra và lưu vào cấu hình runtime và .env."""
        valid, msg = self.test_api_key(api_key)
        if not valid:
            return False, msg

        cleaned_key = api_key.strip()
        self.api_key = cleaned_key
        settings.GEMINI_API_KEY = cleaned_key

        if persist_env:
            try:
                update_env_file("GEMINI_API_KEY", cleaned_key)
            except Exception as e:
                logger.warning(f"[GeminiService] Không thể ghi .env: {e}")

        return True, msg

    def clear_api_key(self, persist_env: bool = True):
        """Xóa API Key về chế độ Local Grounded Engine."""
        self.api_key = ""
        settings.GEMINI_API_KEY = ""
        if persist_env:
            try:
                update_env_file("GEMINI_API_KEY", "")
            except Exception as e:
                logger.warning(f"[GeminiService] Không thể xóa .env: {e}")

    def get_status(self) -> dict:
        """Lấy trạng thái kết nối Gemini hiện tại."""
        configured = self.is_configured()
        masked = None
        primary_model = getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")
        if configured:
            k = self.api_key
            masked = k[:6] + "..." + k[-4:] if len(k) > 10 else "***"
        return {
            "configured": configured,
            "masked_key": masked,
            "model_name": primary_model if configured else "SmartLogis Grounded Analytical Engine",
            "engine": f"Google Gemini LLM ({primary_model})" if configured else "SmartLogis Grounded Analytical Engine (Local CSDL)",
            "message": f"Đang kết nối Google Gemini API Live ({primary_model})" if configured else "Đang sử dụng Bộ Phân Tích CSDL Kho Nội Bộ (Offline/Fallback)"
        }

    def generate_inventory_report(
        self,
        warehouse_data: Dict[str, Any],
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Sinh báo cáo phân tích kho thời gian thực:
        1. Nếu có API Key, gọi Google Gemini API với System Instruction chống ảo giác.
        2. Nếu API gặp sự cố (Rate limit, Timeout, Sai Key, Network down) -> Tự động kích hoạt Local Grounded Fallback Engine.
        """
        # Kiểm tra nếu dữ liệu kho rỗng
        is_empty = warehouse_data.get("metadata", {}).get("is_empty", False)
        if is_empty or warehouse_data.get("metadata", {}).get("total_skus", 0) == 0:
            return self._build_empty_data_response()

        if not self.is_configured():
            logger.warning("[GeminiService] API Key chưa được cấu hình. Kích hoạt Grounded Fallback Engine.")
            return self._generate_grounded_fallback(warehouse_data, reason="API Key chưa được cấu hình")

        # Circuit-breaker: nếu mạng đã bị lỗi ở lần trước, bỏ qua hoàn toàn để không block request
        if self._network_ok is False:
            logger.info("[GeminiService] Circuit-breaker đang mở (đã gặp lỗi mạng trước đó). Dùng Grounded Fallback Engine ngay.")
            return self._generate_grounded_fallback(warehouse_data, reason="Circuit-breaker: Gemini API không khả dụng")

        user_prompt = build_inventory_user_prompt(warehouse_data, output_format=output_format)

        # Thử gọi qua các models hỗ trợ kèm cơ chế retry
        for model_name in SUPPORTED_GEMINI_MODELS:
            result = self._call_gemini_with_retry(model_name, user_prompt)
            if result is not None:
                self._network_ok = True
                parsed_content = self._parse_gemini_response(result, warehouse_data)
                if parsed_content:
                    parsed_content["model_used"] = f"Google Gemini API ({model_name})"
                    parsed_content["is_fallback"] = False
                    return parsed_content
            if getattr(self, "last_error_was_network", False):
                self._network_ok = False
                logger.warning("[GeminiService] Mạng/Timeout không phản hồi. Circuit-breaker đóng, chuyển ngay sang Local Grounded Fallback Engine.")
                break

        # Nếu tất cả các model và retries đều không thành công -> Kích hoạt Fallback
        logger.error("[GeminiService] Tất cả các model Gemini đều không khả dụng. Kích hoạt Local Grounded Fallback Engine.")
        return self._generate_grounded_fallback(warehouse_data, reason="Gemini API Timeout hoặc Quota Limit")

    def _call_gemini_with_retry(
        self,
        model_name: str,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        api_key: Optional[str] = None
    ) -> Optional[str]:
        """
        Gọi Gemini REST API kèm cơ chế Retry với Exponential Backoff.
        """
        key_to_use = (api_key or self.api_key).strip()
        if not key_to_use:
            return None

        base_endpoint = getattr(settings, "GEMINI_API_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
        url = f"{base_endpoint}/models/{model_name}:generateContent?key={key_to_use}"
        
        parts_text = f"{system_prompt}\n\n{user_prompt}" if system_prompt else f"{SYSTEM_PROMPT_ANTI_HALLUCINATION}\n\n{user_prompt}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": parts_text}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "topP": 0.85,
                "maxOutputTokens": 4096
            }
        }

        self.last_error_was_network = False
        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(url, json=payload)
                    
                    if response.status_code == 200:
                        res_json = response.json()
                        candidates = res_json.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            text_parts = [p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p]
                            if text_parts:
                                return "".join(text_parts)
                    
                    elif response.status_code == 429:
                        logger.warning(f"[GeminiService] Gặp mã 429 Rate Limit (Thử lần {attempt}/{self.max_retries}). Chờ backoff...")
                        time.sleep(1.5 * attempt)
                    
                    elif response.status_code in [400, 401, 403]:
                        logger.error(f"[GeminiService] Lỗi xác thực API Key (Mã {response.status_code}): {response.text[:150]}")
                        return None  # Không retry nếu key không hợp lệ
                    
                    elif response.status_code == 404:
                        logger.warning(f"[GeminiService] Model {model_name} không tồn tại hoặc đã lỗi thời (404). Chuyển sang model tiếp theo...")
                        break
                    
                    else:
                        logger.warning(f"[GeminiService] Model {model_name} trả về mã {response.status_code}: {response.text[:150]}")
                        break  # Thử model tiếp theo
            
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                self.last_error_was_network = True
                logger.warning(f"[GeminiService] Lỗi mạng/Timeout khi gọi {model_name} (Thử lần {attempt}/{self.max_retries}): {exc}")
                time.sleep(1.0 * attempt)
            except Exception as e:
                logger.error(f"[GeminiService] Ngoại lệ không xác định khi gọi Gemini: {e}")
                break

        return None

    def _parse_gemini_response(self, raw_text: str, warehouse_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Xử lý và chuẩn hóa chuỗi phản hồi từ Gemini thành cấu trúc dữ liệu hoàn chỉnh.
        """
        cleaned_text = raw_text.strip()
        # Loại bỏ markdown fence ```json nếu có
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        candidates_to_try = [cleaned_text]
        json_match = re.search(r'\{[\s\S]*\}', cleaned_text)
        if json_match and json_match.group(0) != cleaned_text:
            candidates_to_try.append(json_match.group(0))

        try:
            for cand in candidates_to_try:
                try:
                    parsed = json.loads(cand)
                    # Kiểm tra xem có đủ các trường trọng yếu không
                    if "phan_1_tong_quan" in parsed and "phan_2_canh_bao_va_de_xuat_nhap" in parsed:
                        # Nếu thiếu markdown_report, tự sinh từ dữ liệu
                        if not parsed.get("markdown_report"):
                            parsed["markdown_report"] = self._render_markdown_from_json(parsed)
                        return parsed
                except Exception:
                    pass
        except Exception:
            pass

        # Nếu Gemini trả về text thường hoặc Markdown thuần
        logger.info("[GeminiService] Gemini trả về định dạng văn bản Markdown thay vì JSON.")
        return {
            "phan_1_tong_quan": {
                "tong_so_sku": warehouse_data.get("metadata", {}).get("total_skus", 0),
                "so_sku_canh_bao_ton_min": len(warehouse_data.get("low_stock_alerts", [])),
                "so_sku_u_dong_60_ngay": len(warehouse_data.get("dead_stock_items", [])),
                "danh_gia_chung": "Báo cáo phân tích từ Google Gemini LLM."
            },
                "phan_2_canh_bao_va_de_xuat_nhap": warehouse_data.get("low_stock_alerts", [])[:10],
                "phan_3_bien_dong_bat_thuong": {
                    "xuat_dot_bien": warehouse_data.get("high_burn_rate_items", []),
                    "hang_ton_lau_60_ngay": warehouse_data.get("dead_stock_items", [])[:10]
                },
                "insights_widget": self._build_default_insights(warehouse_data),
                "markdown_report": raw_text
            }
        return None

    def _generate_grounded_fallback(self, warehouse_data: Dict[str, Any], reason: str = "") -> Dict[str, Any]:
        """
        Cơ chế Fallback Grounded Engine CSDL nội bộ:
        Tự động phân tích dựa trên dữ liệu thực tế 100%, bảo đảm không ảo giác,
        cung cấp đầy đủ 3 phần khi mất kết nối Gemini.
        """
        meta = warehouse_data.get("metadata", {})
        total_skus = meta.get("total_skus", 0)
        low_stocks = warehouse_data.get("low_stock_alerts", [])
        dead_stocks = warehouse_data.get("dead_stock_items", [])
        high_burns = warehouse_data.get("high_burn_rate_items", [])

        # Phần 1
        phan_1 = {
            "tong_so_sku": total_skus,
            "so_sku_canh_bao_ton_min": len(low_stocks),
            "so_sku_u_dong_60_ngay": len(dead_stocks),
            "danh_gia_chung": (
                f"Hệ thống kho đang quản lý {total_skus} mặt hàng. Ghi nhận {len(low_stocks)} mặt hàng chạm hoặc dưới "
                f"ngưỡng tồn an toàn cần bù đắp, và {len(dead_stocks)} mặt hàng có dấu hiệu tồn đọng lâu ngày."
            )
        }

        # Phần 2
        phan_2 = []
        for item in low_stocks:
            phan_2.append({
                "ma_hh": item["ma_hh"],
                "ten_hh": item["ten_hh"],
                "ton_hien_tai": item["ton_hien_tai"],
                "ton_toi_thieu": item["ton_toi_thieu"],
                "thieu_hut": item["thieu_hut"],
                "burn_rate_ngay": item.get("burn_rate_ngay", 0),
                "so_luong_de_xuat_nhap": item["de_xuat_nhap_them"],
                "muc_do": item["muc_do_nguy_cap"],
                "ly_do": f"Tồn kho {item['ton_hien_tai']}/{item['ton_toi_thieu']} {item['don_vi_tinh']}, thiếu hụt {item['thieu_hut']} đơn vị."
            })

        # Phần 3
        phan_3 = {
            "xuat_dot_bien": high_burns,
            "hang_ton_lau_60_ngay": dead_stocks[:15]
        }

        insights_widget = self._build_default_insights(warehouse_data)

        # Markdown Report
        markdown_content = self._render_fallback_markdown(phan_1, phan_2, phan_3, meta)

        return {
            "model_used": "SmartLogis Grounded Analytical Engine (Fallback)",
            "is_fallback": True,
            "fallback_reason": reason,
            "phan_1_tong_quan": phan_1,
            "phan_2_canh_bao_va_de_xuat_nhap": phan_2,
            "phan_3_bien_dong_bat_thuong": phan_3,
            "insights_widget": insights_widget,
            "markdown_report": markdown_content
        }

    def _build_empty_data_response(self) -> Dict[str, Any]:
        """Phản hồi quy chuẩn khi kho chưa có dữ liệu giao dịch."""
        msg = "Hệ thống chưa ghi nhận dữ liệu giao dịch hợp lệ trong kỳ phân tích (Kho rỗng hoặc chưa phát sinh hoạt động xuất nhập)."
        return {
            "model_used": "SmartLogis Grounded Analytical Engine (Zero Data Rule)",
            "is_fallback": True,
            "phan_1_tong_quan": {
                "tong_so_sku": 0,
                "so_sku_canh_bao_ton_min": 0,
                "so_sku_u_dong_60_ngay": 0,
                "danh_gia_chung": msg
            },
            "phan_2_canh_bao_va_de_xuat_nhap": [],
            "phan_3_bien_dong_bat_thuong": {
                "xuat_dot_bien": [],
                "hang_ton_lau_60_ngay": []
            },
            "insights_widget": [
                {
                    "icon": "fa-solid fa-circle-info text-sky-500",
                    "title": "Chưa Có Dữ Liệu Giao Dịch",
                    "content": msg
                }
            ],
            "markdown_report": f"# BÁO CÁO VẬN HÀNH KHO SMARTLOGIS AI\n\n> [!NOTE]\n> {msg}\n"
        }

    def _build_default_insights(self, warehouse_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Xây dựng 3 cards hiển thị trên Widget Dashboard."""
        low_stocks = warehouse_data.get("low_stock_alerts", [])
        dead_stocks = warehouse_data.get("dead_stock_items", [])
        high_burns = warehouse_data.get("high_burn_rate_items", [])
        total_skus = warehouse_data.get("metadata", {}).get("total_skus", 0)

        critical_names = [x["ten_hh"] for x in low_stocks[:3]]
        critical_str = ", ".join(critical_names) if critical_names else "Không có SKU thiếu hụt nghiêm trọng"

        return [
            {
                "icon": "fa-solid fa-triangle-exclamation text-amber-500",
                "title": f"Cảnh Báo Tồn Min ({len(low_stocks)}/{total_skus} SKU)",
                "content": f"Khuyến nghị ưu tiên lập Phiếu Nhập Kho cho các mặt hàng: {critical_str}."
            },
            {
                "icon": "fa-solid fa-fire-flame-curved text-rose-500",
                "title": f"Biến Động Tốc Độ Xuất ({len(high_burns)} SKU tăng mạnh)",
                "content": f"Ghi nhận {len(high_burns)} mặt hàng có tốc độ tiêu thụ cao (> 2 đơn vị/ngày). Cần theo dõi sát mức dữ trữ an toàn."
            },
            {
                "icon": "fa-solid fa-box-archive text-emerald-500",
                "title": f"Hàng Tồn Ứ Đọng Lâu (> 60 ngày)",
                "content": f"Có {len(dead_stocks)} SKU không phát sinh xuất kho trên 60 ngày. Cần phương án thanh lý hoặc tối ưu diện tích lưu kho."
            }
        ]

    def _render_fallback_markdown(self, p1: dict, p2: list, p3: dict, meta: dict) -> str:
        lines = [
            "# BÁO CÁO PHÂN TÍCH VẬN HÀNH KHO THỜI GIAN THỰC (SMARTLOGIS AI)",
            f"*Thời điểm kết xuất: {meta.get('extracted_at', 'N/A')} | Kỳ phân tích: 30 ngày gần nhất*",
            "",
            "## Phần 1: Tình Trạng Tồn Kho Tổng Quan",
            f"- **Tổng số mặt hàng (SKU) quản lý**: {p1.get('tong_so_sku', 0)} SKU.",
            f"- **Số SKU chạm/dưới ngưỡng tồn tối thiểu**: {p1.get('so_sku_canh_bao_ton_min', 0)} SKU (Cần can thiệp nhập hàng).",
            f"- **Số SKU tồn đọng > 60 ngày**: {p1.get('so_sku_u_dong_60_ngay', 0)} SKU.",
            f"- **Đánh giá tổng quan**: {p1.get('danh_gia_chung', '')}",
            "",
            "## Phần 2: Cảnh Báo & Gợi Ý Nhập Hàng Khẩn Cấp",
            "| Mã HH | Tên Hàng Hóa | Tồn Hiện Tại | Tồn Min | Thiếu Hụt | Tốc Độ Xuất/Ngày | Đề Xuất Nhập | Mức Độ |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
        ]

        if not p2:
            lines.append("| - | *Tất cả mặt hàng đang ở mức an toàn* | - | - | - | - | - | AN_TOAN |")
        else:
            for item in p2:
                lines.append(
                    f"| {item['ma_hh']} | {item['ten_hh']} | {item['ton_hien_tai']} | {item['ton_toi_thieu']} | "
                    f"{item['thieu_hut']} | {item.get('burn_rate_ngay', 0)} | **+{item['so_luong_de_xuat_nhap']}** | {item['muc_do']} |"
                )

        lines.extend([
            "",
            "## Phần 3: Tóm Tắt Biến Động Bất Thường",
            "### 3.1. Hàng Hóa Tiêu Thụ Tăng Mạnh (High Burn Rate)",
        ])

        high_burns = p3.get("xuat_dot_bien", [])
        if not high_burns:
            lines.append("- Không ghi nhận SKU nào có tốc độ xuất kho đột biến vượt ngưỡng trong kỳ.")
        else:
            for hb in high_burns:
                lines.append(f"- **{hb['ten_hh']}** (Mã `{hb['ma_hh']}`): Xuất {hb.get('tong_xuat_30d', 0)} đơn vị/30 ngày (Trung bình {hb.get('burn_rate_ngay', 0)} đơn vị/ngày). Tồn hiện tại: {hb.get('ton_kho_hien_tai', 0)}.")

        lines.extend([
            "",
            "### 3.2. Hàng Tồn Kho Lâu Ngày (> 60 ngày không phát sinh xuất kho)",
        ])

        dead_stocks = p3.get("hang_ton_lau_60_ngay", [])
        if not dead_stocks:
            lines.append("- Tốc độ luân chuyển kho tốt, không có hàng tồn đọng quá 60 ngày.")
        else:
            for ds in dead_stocks[:10]:
                lines.append(f"- **{ds['ten_hh']}** (Mã `{ds['ma_hh']}`): Tồn đọng `{ds.get('ton_kho_u_dong', 0)}` {ds.get('don_vi_tinh', '')}, không xuất hàng trong `{ds.get('so_ngay_khong_xuat', 0)}` ngày.")

        return "\n".join(lines)

    def _render_markdown_from_json(self, parsed: dict) -> str:
        return self._render_fallback_markdown(
            parsed.get("phan_1_tong_quan", {}),
            parsed.get("phan_2_canh_bao_va_de_xuat_nhap", []),
            parsed.get("phan_3_bien_dong_bat_thuong", {}),
            {"extracted_at": "Thời gian thực"}
        )


# Singleton instance
gemini_service = GeminiService()
