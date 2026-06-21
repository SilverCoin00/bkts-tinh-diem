from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from program_data import programs_data # Import data từ file data.py (hoặc đọc từ JSON)

router = APIRouter()

# 1. Định nghĩa cấu trúc dữ liệu nhận từ Frontend (Tương đương interface ScoreResult)
class Combination(BaseModel):
    code: str
    score: float

class ScoreResultInput(BaseModel):
    xetTuyenTN: Optional[float] = None
    diemTSA: Optional[float] = None
    diemXTTN12: Optional[float] = None
    combinations: List[Combination] = []

# 2. Logic tính toán và trả kết quả
@router.post("/api/suggest-programs")
def suggest_programs(results: ScoreResultInput):
    suitable_programs = []
    K01_SUB_COMBOS = ["K01_LY", "K01_HOA", "K01_SINH", "K01_TIN"]

    for prog in programs_data:
        is_eligible = False
        highest_score = 0.0

        # Tiêu chí 1: XTTN 1.3
        if results.xetTuyenTN is not None and prog.get("xttn3Predict") is not None:
            if results.xetTuyenTN >= prog["xttn3Predict"]:
                is_eligible = True
                highest_score = max(highest_score, results.xetTuyenTN)

        # Tiêu chí 2: TSA
        if results.diemTSA is not None and prog.get("tsaPredict") is not None:
            if results.diemTSA >= prog["tsaPredict"]:
                is_eligible = True
                highest_score = max(highest_score, results.diemTSA)

        # Tiêu chí 3: XTTN 1.2
        if results.diemXTTN12 is not None and prog.get("xttn2Predict") is not None:
            if results.diemXTTN12 >= prog["xttn2Predict"]:
                is_eligible = True
                highest_score = max(highest_score, results.diemXTTN12)

        # Tiêu chí 4: Tổ hợp môn
        prog_combos = prog.get("combinations", [])
        admission_predict = prog.get("admissionPredict")

        if admission_predict is not None and prog_combos:
            for user_combo in results.combinations:
                is_match = False
                
                # Kiểm tra tổ hợp con của K01
                if user_combo.code in K01_SUB_COMBOS and "K01" in prog_combos:
                    if user_combo.score >= admission_predict:
                        is_match = True
                # Kiểm tra tổ hợp bình thường
                elif user_combo.code in prog_combos:
                    if user_combo.score >= admission_predict:
                        is_match = True

                if is_match:
                    is_eligible = True
                    highest_score = max(highest_score, user_combo.score)

        # Nếu thoả mãn ít nhất 1 tiêu chí, đưa vào danh sách phù hợp
        if is_eligible:
            matched_prog = prog.copy() # Tránh thay đổi data gốc
            matched_prog["calculatedScore"] = highest_score
            suitable_programs.append(matched_prog)

    # Danh sách các mã ngành ưu tiên đặc biệt lên đầu (tùy chỉnh)
    CUSTOM_PRIORITIZED_CODES = ["ET1"]

    # 3. Thuật toán Sắp xếp (Ưu tiên các mã ưu tiên tùy chỉnh -> Ngành điện -> Ngành khác)
    def sort_key(p):
        code = p.get("code")
        # Tìm xem code có khớp tiền tố (hoặc khớp hoàn toàn) với mã ưu tiên nào không
        prioritized_idx = next((i for i, prioritized_code in enumerate(CUSTOM_PRIORITIZED_CODES) if code.startswith(prioritized_code)), None)
        if prioritized_idx is not None:
            # Ưu tiên tuyệt đối lên đầu, xếp theo thứ tự trong danh sách, tiếp theo là điểm calculatedScore giảm dần
            score = p.get("calculatedScore") or 0.0
            return (0, prioritized_idx, -score)
            
        is_electrical = p.get("isElectrical", False)
        # Python sort tăng dần. Mẹo: dùng số âm để sort giảm dần.
        if is_electrical:
            score = p.get("admissionPredict") or 0.0
            return (1, 0, -score)
        else:
            score = p.get("tsaPredict") or 0.0
            return (2, 0, -score)

    suitable_programs.sort(key=sort_key)

    # 4. Hậu xử lý (Post-processing) cho các ngành mới: ED5, FL4, CH-E20, MI-E22, EM-E17
    # Luôn đứng sau ngành có điểm cao nhất của cùng mã chữ đầu
    SPECIAL_NEW_CODES = {"ED5", "FL4", "CH-E20", "MI-E22", "EM-E17"}
    
    special_progs = [p for p in suitable_programs if p.get("code") in SPECIAL_NEW_CODES]
    normal_progs = [p for p in suitable_programs if p.get("code") not in SPECIAL_NEW_CODES]
    
    import re
    for p in special_progs:
        # Lấy mã chữ đầu (ví dụ: "ED5" -> "ED", "CH-E20" -> "CH")
        m = re.match(r"^([a-zA-Z]+)", p.get("code", ""))
        prefix = m.group(1) if m else ""
        
        if prefix:
            target_index = -1
            for idx, np in enumerate(normal_progs):
                nm = re.match(r"^([a-zA-Z]+)", np.get("code", ""))
                np_prefix = nm.group(1) if nm else ""
                if np_prefix == prefix:
                    target_index = idx
                    break
            
            if target_index != -1:
                normal_progs.insert(target_index + 1, p)
            else:
                normal_progs.append(p)
        else:
            normal_progs.append(p)
            
    suitable_programs = normal_progs

    return suitable_programs

# Chạy server: uvicorn main:app --reload