import re
from models import Reader
import data_handler
from datetime import datetime

# KIỂM TRA SỐ ĐIỆN THOẠI HỢP LỆ
def _validate_phone(so_dien_thoai):
    sdt = str(so_dien_thoai).strip()
    if not (len(sdt) == 10 and sdt.isdigit() and sdt.startswith("0")):
        raise ValueError("Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0.")

# KIỂM TRA NGÀY SINH HỢP LỆ
def _validate_date(ngay_sinh):
    try:
        birth_date = datetime.strptime(ngay_sinh, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(
            "Ngày sinh phải có dạng dd/mm/yyyy (ví dụ: 20/06/2008)."
        )
    if birth_date >= datetime.now().date():
        raise ValueError("Ngày sinh phải nhỏ hơn ngày hiện tại.")

# THÊM BẠN ĐỌC MỚI
def add_reader(ma_ban_doc, ho_ten, ngay_sinh, gioi_tinh, dia_chi, chuc_vu, so_dien_thoai):
    """
    Thêm bạn đọc mới.
    Raise ValueError nếu dữ liệu không hợp lệ.
    """
    ma_ban_doc = str(ma_ban_doc).strip()

    if not re.fullmatch(r"BD\d+", ma_ban_doc):
        raise ValueError("Mã bạn đọc phải có dạng BD + số (ví dụ: BD001)")

    if not all([ma_ban_doc, ho_ten, gioi_tinh, dia_chi, chuc_vu, so_dien_thoai]):
        raise ValueError("Các trường bắt buộc không được để trống.")

    if ma_ban_doc in data_handler.readers_db:
        raise ValueError(f"Mã bạn đọc '{ma_ban_doc}' đã tồn tại.")

    _validate_phone(so_dien_thoai)
    _validate_date(ngay_sinh)

    new_reader = Reader(
        ma_ban_doc=ma_ban_doc, ho_ten=ho_ten, ngay_sinh=ngay_sinh,
        gioi_tinh=gioi_tinh, dia_chi=dia_chi, chuc_vu = chuc_vu, so_dien_thoai=so_dien_thoai
    )
    data_handler.readers_db[ma_ban_doc] = new_reader
    data_handler.save_data()
    return new_reader

# CẬP NHẬT THÔNG TIN BẠN ĐỌC 
def update_reader(ma_ban_doc, ho_ten, ngay_sinh, gioi_tinh, dia_chi, chuc_vu, so_dien_thoai):
    """
    Cập nhật thông tin bạn đọc (không đổi mã).
    Raise ValueError nếu không tìm thấy hoặc dữ liệu không hợp lệ.
    """
    ma_ban_doc = str(ma_ban_doc).strip()

    if not all([ho_ten, gioi_tinh, dia_chi, chuc_vu, so_dien_thoai]):
        raise ValueError("Các trường thông tin bắt buộc không được để trống.")

    _validate_phone(so_dien_thoai)
    _validate_date(ngay_sinh)

    reader = data_handler.readers_db[ma_ban_doc]
    reader.ho_ten        = ho_ten
    reader.ngay_sinh     = ngay_sinh
    reader.gioi_tinh     = gioi_tinh
    reader.dia_chi       = dia_chi
    reader.chuc_vu       = chuc_vu
    reader.so_dien_thoai = so_dien_thoai

    data_handler.save_data()
    return reader

# XÓA BẠN ĐỌC 
def delete_reader(ma_ban_doc):
    """
    Xóa bạn đọc.
    Raise ValueError nếu không tìm thấy hoặc đang mượn sách.
    """
    ma_ban_doc = str(ma_ban_doc).strip()

    dang_muon = [
        r for r in data_handler.tracking_records
        if r.ma_ban_doc == ma_ban_doc and r.trang_thai in ("Đang mượn", "Quá hạn")
    ]
    if dang_muon:
        co_qua_han = any(r.trang_thai == "Quá hạn" for r in dang_muon)
        msg = "Không thể xóa bạn đọc đang mượn sách"
        if co_qua_han:
            msg += " (có sách quá hạn)"
        raise ValueError(msg + ".")

    del data_handler.readers_db[ma_ban_doc]
    data_handler.save_data()

# TÌM KIẾM BẠN ĐỌC 
def search_readers(keyword, field="ho_ten"):
    """
    Tìm kiếm bạn đọc theo field và keyword.
    field: 'ma_ban_doc' | 'ho_ten' | 'so_dien_thoai' | 'chuc_vu' |'dia_chi'
    Trả về list[Reader].
    """
    kw = keyword.strip().lower()
    field_map = {
        "ma_ban_doc":    lambda r: str(r.ma_ban_doc).lower(),
        "ho_ten":        lambda r: str(r.ho_ten).lower(),
        "so_dien_thoai": lambda r: str(r.so_dien_thoai).lower(),
        "chuc_vu"      : lambda r: str(r.chuc_vu).lower(),
        "dia_chi":       lambda r: str(r.dia_chi).lower(),
    }
    get_val = field_map.get(field, lambda r: "")
    return [r for r in data_handler.readers_db.values() if kw in get_val(r)]

# LỌC VÀ SẮP XẾP DANH SÁCH
def get_all_readers():
    """Trả về list[Reader] toàn bộ bạn đọc."""
    return list(data_handler.readers_db.values())

def filter_readers(gioi_tinh=None, dia_chi=None, chuc_vu=None):
    """
    Lọc bạn đọc theo giới tính và/hoặc địa chỉ.
    Trả về list[Reader].
    """
    readers = get_all_readers()
    if gioi_tinh and gioi_tinh != "Tất cả":
        readers = [r for r in readers if r.gioi_tinh == gioi_tinh]
    if dia_chi and dia_chi != "Tất cả":
        readers = [r for r in readers if r.dia_chi == dia_chi]
    if chuc_vu and chuc_vu != "Tất cả":
        readers = [r for r in readers if r.chuc_vu == chuc_vu]
    return readers


