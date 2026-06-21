from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from languageconversion import get_conversion_logic # Tái sử dụng hàm từ file kia
from subject_combinations_data import subject_combinations_data

router = APIRouter()

# 1. DATA TỔ HỢP MÔN

# 2. MODELS DỮ LIỆU ĐẦU VÀO TỪ FRONTEND
class THPTScoresInput(BaseModel):
    toan: Optional[float] = None
    van: Optional[float] = None
    ly: Optional[float] = None
    hoa: Optional[float] = None
    tin: Optional[float] = None
    sinh: Optional[float] = None
    anh: Optional[float] = None
    nhat: Optional[float] = None
    phap: Optional[float] = None
    trung: Optional[float] = None
    duc: Optional[float] = None
    han: Optional[float] = None # Thêm trường dành cho Tiếng Hàn (TOPIK)

class LanguageCertInput(BaseModel):
    type: str
    score: str
    bonusScore: Optional[float] = None

class AdmissionScoresInput(BaseModel):
    diem13: Optional[float] = None
    diemTSA: Optional[float] = None
    diemXTTN12: Optional[float] = None
    thptScores: THPTScoresInput
    languageCertificates: Optional[List[LanguageCertInput]] = None
    khuvuc: Optional[str] = None
    doituongUT: Optional[str] = None

# 3. HELPER FUNCTIONS
def get_khuvuc_score(khuvuc: Optional[str]) -> float:
    mapping = {"KV1": 0.75, "KV2-NT": 0.5, "KV2": 0.25, "KV3": 0}
    return mapping.get(khuvuc, 0.0)

def get_doituong_score(doituong: Optional[str]) -> float:
    if doituong in ["01", "02", "03", "04"]: return 2.0
    if doituong in ["05", "06", "07"]: return 1.0
    return 0.0

# 4. API TÍNH TOÁN
@router.post("/api/calculate-admission")
def calculate_admission(scores: AdmissionScoresInput):
    kv_score = get_khuvuc_score(scores.khuvuc)
    dt_score = get_doituong_score(scores.doituongUT)
    
    language_bonus = 0.0
    language_subj_score = 0.0

    # Xử lý danh sách điểm ngoại ngữ (Gọi trực tiếp hàm từ languageconversion.py)
    max_language_bonus = 0.0

    if scores.languageCertificates:
        for cert in scores.languageCertificates:
            c_type = cert.type
            c_score = cert.score
            
            if c_type == "TOEIC" and cert.bonusScore is not None:
                current_bonus = cert.bonusScore
                language_subj_score = float(c_score)
            else:
                conv = get_conversion_logic(c_type, c_score)
                current_bonus = conv["bonusScore"]
                language_subj_score = conv["convertedScore"]
            
            # Chọn bonus score lớn nhất phục vụ cho TSA
            if current_bonus > max_language_bonus:
                max_language_bonus = current_bonus

            # Ghi đè điểm ngoại ngữ vào thptScores
            if "JLPT" in c_type:
                scores.thptScores.nhat = max(scores.thptScores.nhat or 0, language_subj_score)
            elif any(x in c_type for x in ["DELF", "TCF"]):
                scores.thptScores.phap = max(scores.thptScores.phap or 0, language_subj_score)
            elif any(x in c_type for x in ["HSK", "HSKK"]):
                scores.thptScores.trung = max(scores.thptScores.trung or 0, language_subj_score)
            elif any(x in c_type for x in ["Goethe", "TestDaF", "DSH", "DSD"]):
                # Match Goethe/ÖSD/telc/ECL, TestDaF, DSH, DSD (both unicode Ö and ASCII O variants)
                scores.thptScores.duc = max(scores.thptScores.duc or 0, language_subj_score)
            elif "TOPIK" in c_type:
                # Cập nhật thêm nhóm chứng chỉ Tiếng Hàn theo bảng quy đổi tuyển sinh 2026
                scores.thptScores.han = max(scores.thptScores.han or 0, language_subj_score)
            else:
                # Bao gồm IELTS, TOEFL, Aptis ESOL, PEIC, Linguaskill, Cambridge English...
                scores.thptScores.anh = max(scores.thptScores.anh or 0, language_subj_score)

            # QUY ĐỔI ĐIỂM NGOẠI NGỮ KHÁC SANG ANH CHO A01, D01, D07:
            # Tất cả chứng chỉ ngoại ngữ (Nhật, Pháp, Trung, Đức, Hàn...) đều có thể quy đổi thành môn Tiếng Anh
            # để xét các tổ hợp A01, D01, D07. Do đó ghi đè thêm vào môn Anh.
            scores.thptScores.anh = max(scores.thptScores.anh or 0, language_subj_score)

    result = {"combinations": []}

    # Tính điểm 1.3 (chỉ có ý nghĩa khi raw <= 100; cap input ở mức 100)
    if scores.diem13 is not None:
        raw = min(100.0, scores.diem13)
        priority = max(0.0, (kv_score + dt_score) * ((100 - raw)/25) * (10/3)) if raw >= 75 else (kv_score + dt_score) * (10/3)
        result["xetTuyenTN"] = round(raw + priority, 2)
        
    # Tính điểm 1.2 (càng ống: cap tại 100)
    if scores.diemXTTN12 is not None:
        raw = min(100.0, scores.diemXTTN12)
        priority = max(0.0, (kv_score + dt_score) * ((100 - raw)/25) * (10/3)) if raw >= 75 else (kv_score + dt_score) * (10/3)
        result["diemXTTN12"] = round(raw + priority, 2)

    # Tính điểm TSA
    if scores.diemTSA is not None:
        raw = min(100.0, scores.diemTSA + max_language_bonus)
        priority = max(0.0, (kv_score + dt_score) * ((100 - raw)/25) * (10/3)) if raw >= 75 else (kv_score + dt_score) * (10/3)
        result["diemTSA"] = round(raw + priority, 2)

    # Tính điểm Tổ hợp môn
    thpt_dict = scores.thptScores.model_dump() # Lấy dict dữ liệu môn
    
    for combo in subject_combinations_data:
        # Nếu nhập đủ điểm các môn trong tổ hợp
        if all(thpt_dict.get(subj) is not None for subj in combo["subjects"]):
            base_score = 0.0
            code = combo["code"]
            
            if code.startswith("K01"):
                toan = thpt_dict.get("toan", 0)
                van = thpt_dict.get("van", 0)
                mon3 = thpt_dict.get(combo["subjects"][2], 0)
                base_score = (toan * 3 + van * 1 + mon3 * 2) * 0.5
            elif "mainSubject" in combo:
                s1 = thpt_dict.get(combo["subjects"][0], 0)
                s2 = thpt_dict.get(combo["subjects"][1], 0)
                s3 = thpt_dict.get(combo["subjects"][2], 0)
                main_val = thpt_dict.get(combo["mainSubject"], 0)
                base_score = (s1 + s2 + s3 + main_val) * 0.75
            else:
                s1 = thpt_dict.get(combo["subjects"][0], 0)
                s2 = thpt_dict.get(combo["subjects"][1], 0)
                s3 = thpt_dict.get(combo["subjects"][2], 0)
                base_score = s1 + s2 + s3

            if base_score >= 22.5:
                priority_score = max(0.0, ((30 - base_score) / 7.5) * (kv_score + dt_score))
            else:
                priority_score = kv_score + dt_score

            result["combinations"].append({
                "code": code,
                "score": round(base_score + priority_score, 2)
            })

    return result
