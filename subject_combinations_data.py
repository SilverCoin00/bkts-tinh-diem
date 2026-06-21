subject_combinations_data = [
    {"code": "A00", "subjects": ["toan", "ly", "hoa"], "mainSubject": "toan"},
    {"code": "A01", "subjects": ["toan", "ly", "anh"], "mainSubject": "toan"},
    
    # A01 cho các ngôn ngữ còn lại (quy đổi tương đương môn Anh)
    {"code": "A01_JPN", "subjects": ["toan", "ly", "nhat"], "mainSubject": "toan"},
    {"code": "A01_FRA", "subjects": ["toan", "ly", "phap"], "mainSubject": "toan"},
    {"code": "A01_CHN", "subjects": ["toan", "ly", "trung"], "mainSubject": "toan"},
    {"code": "A01_GER", "subjects": ["toan", "ly", "duc"], "mainSubject": "toan"},
    {"code": "A01_KOR", "subjects": ["toan", "ly", "han"], "mainSubject": "toan"},

    {"code": "K01_LY", "subjects": ["toan", "van", "ly"]},
    {"code": "K01_HOA", "subjects": ["toan", "van", "hoa"]},
    {"code": "K01_SINH", "subjects": ["toan", "van", "sinh"]},
    {"code": "K01_TIN", "subjects": ["toan", "van", "tin"]},
    {"code": "B00", "subjects": ["toan", "hoa", "sinh"], "mainSubject": "toan"},
    {"code": "D01", "subjects": ["toan", "van", "anh"], "mainSubject": "toan"},
    {"code": "D07", "subjects": ["toan", "hoa", "anh"], "mainSubject": "toan"},
    {"code": "DD2", "subjects": ["toan", "van", "han"], "mainSubject": "han"},
    {"code": "D01_FL1,2,3", "subjects": ["toan", "van", "anh"], "mainSubject": "anh"},
    {"code": "D04_FL1,2,3", "subjects": ["toan", "van", "trung"], "mainSubject": "trung"},
    
    # Các tổ hợp KHÔNG có môn chính
    {"code": "A00_KHONG_CO_MON_CHINH", "subjects": ["toan", "ly", "hoa"]},
    {"code": "A01_KHONG_CO_MON_CHINH", "subjects": ["toan", "ly", "anh"]},
    
    # KHÔNG MÔN CHÍNH cho A01 các ngôn ngữ còn lại
    {"code": "A01_JPN_KHONG_CO_MON_CHINH", "subjects": ["toan", "ly", "nhat"]},
    {"code": "A01_FRA_KHONG_CO_MON_CHINH", "subjects": ["toan", "ly", "phap"]},
    {"code": "A01_CHN_KHONG_CO_MON_CHINH", "subjects": ["toan", "ly", "trung"]},
    {"code": "A01_GER_KHONG_CO_MON_CHINH", "subjects": ["toan", "ly", "duc"]},
    {"code": "A01_KOR_KHONG_CO_MON_CHINH", "subjects": ["toan", "ly", "han"]},

    {"code": "B00_KHONG_CO_MON_CHINH", "subjects": ["toan", "hoa", "sinh"]},
    {"code": "D01_KHONG_CO_MON_CHINH", "subjects": ["toan", "van", "anh"]},
    {"code": "D04_KHONG_CO_MON_CHINH", "subjects": ["toan", "van", "trung"]},
    {"code": "D07_KHONG_CO_MON_CHINH", "subjects": ["toan", "hoa", "anh"]},
    {"code": "DD2_KHONG_CO_MON_CHINH", "subjects": ["toan", "van", "han"]}
]