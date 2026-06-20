import re
from models import Book
import data_handler

# THÊM SÁCH 
def add_book(ma_sach, ten_sach, tac_gia, the_loai,
             so_luong_sach, tinh_trang_sach, nha_xuat_ban, nam_xuat_ban):
    """
    Thêm sách mới vào hệ thống.
    Raise ValueError nếu dữ liệu không hợp lệ.
    """
    ma_sach = str(ma_sach).strip()
    if not re.fullmatch(r"S\d+", ma_sach):
        raise ValueError("Mã sách phải có dạng S + số.")
    
    nam_xuat_ban = str(nam_xuat_ban).strip()
    if not re.fullmatch(r"\d{4}", nam_xuat_ban):
        raise ValueError("Năm xuất bản phải là một số có 4 chữ số.")

    if not all([ma_sach, ten_sach, tac_gia, the_loai, tinh_trang_sach]):
        raise ValueError("Các trường bắt buộc không được để trống.")

    if ma_sach in data_handler.books_db:
        raise ValueError(f"Mã sách '{ma_sach}' đã tồn tại trong hệ thống.")

    try:
        so_luong = int(so_luong_sach)
    except (ValueError, TypeError):
        raise ValueError("Số lượng sách không hợp lệ.")
    if so_luong <= 0:
        raise ValueError("Số lượng sách phải lớn hơn 0.")

    new_book = Book(
        ma_sach=ma_sach, ten_sach=ten_sach, tac_gia=tac_gia,
        the_loai=the_loai, so_luong_sach=so_luong,
        tinh_trang_sach=tinh_trang_sach,
        nha_xuat_ban=nha_xuat_ban, nam_xuat_ban=nam_xuat_ban
    )
    data_handler.books_db[ma_sach] = new_book
    data_handler.save_data()
    return new_book

# CẬP NHẬT SÁCH 
def update_book(ma_sach, ten_sach, tac_gia, the_loai,
                so_luong_sach, tinh_trang_sach, nha_xuat_ban, nam_xuat_ban):
    """
    Cập nhật thông tin sách (không đổi mã sách).
    Raise ValueError nếu không tìm thấy hoặc dữ liệu không hợp lệ.
    """
    ma_sach = str(ma_sach).strip()

    if not all([ten_sach, tac_gia, the_loai, tinh_trang_sach]):
        raise ValueError("Các trường bắt buộc không được để trống.")
    
    nam_xuat_ban = str(nam_xuat_ban).strip()
    if not re.fullmatch(r"\d{4}", nam_xuat_ban):
        raise ValueError("Năm xuất bản phải là một số có 4 chữ số.")

    try:
        so_luong = int(so_luong_sach)
    except (ValueError, TypeError):
        raise ValueError("Số lượng sách không hợp lệ.")
    if so_luong <= 0:
        raise ValueError("Số lượng sách phải lớn hơn 0")

    # Không để số lượng mới < số đang cho mượn
    so_dang_muon = sum(
        1 for r in data_handler.tracking_records
        if r.ma_sach == ma_sach and r.trang_thai in ("Đang mượn", "Quá hạn")
    )
    if so_luong < so_dang_muon:
        raise ValueError(
            f"Số lượng mới cập nhật là ({so_luong}) không thể ít hơn "
            f"số sách đang cho mượn là ({so_dang_muon})."
        )

    book = data_handler.books_db[ma_sach]
    book.ten_sach       = ten_sach
    book.tac_gia        = tac_gia
    book.the_loai       = the_loai
    book.nha_xuat_ban   = nha_xuat_ban
    book.nam_xuat_ban   = nam_xuat_ban
    book.so_luong_sach  = so_luong
    book.tinh_trang_sach = tinh_trang_sach

    # Đồng bộ tên sách trong lịch sử mượn
    for r in data_handler.tracking_records:
        if r.ma_sach == ma_sach:
            r.ten_sach = ten_sach

    data_handler.save_data()
    return book

# XÓA SÁCH 
def delete_book(ma_sach):
    """
    Xóa sách khỏi hệ thống.
    Raise ValueError nếu không tìm thấy hoặc sách đang được mượn.
    """
    ma_sach = str(ma_sach).strip()

    dang_muon = [
        r for r in data_handler.tracking_records
        if str(r.ma_sach) == ma_sach and r.trang_thai in ("Đang mượn", "Quá hạn")
    ]
    if dang_muon:
        raise ValueError("Không thể xóa sách đang được mượn.")

    del data_handler.books_db[ma_sach]
    data_handler.save_data()

# TÌM KIẾM SÁCH 
def search_books(keyword, field="ten_sach"):
    """
    Tìm kiếm sách theo keyword (không phân biệt hoa thường).
    Trả về list[Book].
    """
    kw = keyword.strip().lower()
    field_map = {
        "ma_sach":      lambda b: str(b.ma_sach).lower(),
        "ten_sach":     lambda b: str(b.ten_sach).lower(),
        "tac_gia":      lambda b: str(b.tac_gia).lower(),
        "the_loai":     lambda b: str(b.the_loai).lower(),
        "nha_xuat_ban": lambda b: str(b.nha_xuat_ban).lower(),
    }
    get_val = field_map.get(field, lambda b: "")
    return [b for b in data_handler.books_db.values() if kw in get_val(b)]

# LỌC VÀ SẮP XẾP DANH SÁCH
def get_all_books():
    """Trả về list[Book] toàn bộ sách."""
    return list(data_handler.books_db.values())

def filter_books(the_loai=None, tac_gia=None, nha_xuat_ban=None, tinh_trang_sach=None):
    """
    Lọc sách theo các tiêu chí 
    Trả về list[Book].
    """
    books = get_all_books()
    if the_loai and the_loai != "Tất cả":
        books = [b for b in books if b.the_loai == the_loai]
    if tac_gia and tac_gia != "Tất cả":
        books = [b for b in books if b.tac_gia == tac_gia]
    if nha_xuat_ban and nha_xuat_ban != "Tất cả":
        books = [b for b in books if b.nha_xuat_ban == nha_xuat_ban]
    if tinh_trang_sach and tinh_trang_sach != "Tất cả":
        books = [b for b in books if b.tinh_trang_sach == tinh_trang_sach]
    return books
