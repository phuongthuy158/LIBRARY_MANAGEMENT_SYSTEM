from datetime import datetime, date
from models import TrackBook
import data_handler

# SỐ LƯỢNG CÒN LẠI (tính động)
def get_so_luong_con_lai(ma_sach):
    """
    Trả về số sách còn lại trong thư viện:
    = so_luong_sach - số bản ghi đang mượn/quá hạn của sách đó.
    """
    book = data_handler.books_db.get(ma_sach)
    if book is None:
        return 0
    so_dang_muon = sum(
        1 for r in data_handler.tracking_records
        if r.ma_sach == str(ma_sach) and r.trang_thai in ("Đang mượn", "Quá hạn")
    )
    return max(0, book.so_luong_sach - so_dang_muon)


# KIỂM TRA & CẬP NHẬT SÁCH QUÁ HẠN 
def update_overdue_status():
    """
    Duyệt toàn bộ bản ghi 'Đang mượn', chuyển sang 'Quá hạn'
    nếu quá số ngày cho mượn tối đa.
    """
    today = date.today()
    changed = False

    for record in data_handler.tracking_records:
        if record.trang_thai == "Đang mượn":
            reader = data_handler.readers_db.get(record.ma_ban_doc)
            chuc_vu = reader.chuc_vu if reader else ""
            if chuc_vu == "Giảng viên":
                try:
                    ngay_muon = datetime.strptime(record.ngay_muon, "%d/%m/%Y").date()
                    if (today - ngay_muon).days > 90:
                        record.trang_thai = "Quá hạn"
                        changed = True
                except ValueError:
                    pass
            if chuc_vu == "Sinh viên" or chuc_vu == "Khác":
                try:
                    ngay_muon = datetime.strptime(record.ngay_muon, "%d/%m/%Y").date()
                    if (today - ngay_muon).days > 30:
                        record.trang_thai = "Quá hạn"
                        changed = True
                except ValueError:
                    pass
    if changed:
        data_handler.save_data()

# MƯỢN SÁCH 
def borrow_book(ma_ban_doc, ma_sach, chuc_vu):
    """
    Xử lý mượn sách.
    Raise ValueError nếu vi phạm bất kỳ điều kiện nào.
    Trả về TrackBook vừa tạo.
    """
    ma_ban_doc = str(ma_ban_doc).strip()
    ma_sach    = str(ma_sach).strip()
    chuc_vu    = str(chuc_vu).strip()

    # Kiểm tra tồn tại
    if ma_ban_doc not in data_handler.readers_db:
        raise ValueError(f"Mã bạn đọc '{ma_ban_doc}' không tồn tại.")
    if ma_sach not in data_handler.books_db:
        raise ValueError(f"Mã sách '{ma_sach}' không tồn tại.")

    book = data_handler.books_db[ma_sach]

    # Kiểm tra số sách còn lại trong thư viện (tổng - đang mượn - quá hạn)
    if get_so_luong_con_lai(ma_sach) <= 0:
        raise ValueError(f"Cuốn sách '{book.ten_sach}' không còn sẵn trong thư viện.")

    # Kiểm tra giới hạn mượn của bạn đọc
    so_dang_muon = sum(
        1 for r in data_handler.tracking_records
        if r.ma_ban_doc == ma_ban_doc and r.trang_thai in ("Đang mượn", "Quá hạn")
    )
    so_qua_han = sum(
        1 for r in data_handler.tracking_records
        if r.ma_ban_doc == ma_ban_doc and r.trang_thai == "Quá hạn"
    )

    if chuc_vu == "Giảng viên" and so_dang_muon > 20:
        raise ValueError(f"Bạn đọc đã mượn tối đa số sách cho phép, không thể tiến hành mượn thêm.")
    if chuc_vu == "Giảng viên" and so_qua_han > 10:
        raise ValueError(
            f"Bạn đọc đang có {so_qua_han} cuốn quá hạn, không thể tiến hành mượn thêm."
        )

    if (chuc_vu == "Sinh viên" or chuc_vu == "Khác") and so_dang_muon > 10:
        raise ValueError(f"Bạn đọc đã mượn tối đa số sách cho phép, không thể tiến hành mượn thêm.")
    if (chuc_vu == "Sinh viên" or chuc_vu == "Khác") and so_qua_han > 5:
        raise ValueError(
            f"Bạn đọc đang có {so_qua_han} cuốn quá hạn, không thể tiến hành mượn thêm."
        )
    
    # Kiểm tra trùng lặp
    trung_lap = any(
        r for r in data_handler.tracking_records
        if r.ma_ban_doc == ma_ban_doc
        and r.ma_sach == ma_sach
        and r.trang_thai in ("Đang mượn", "Quá hạn")
    )
    if trung_lap:
        raise ValueError("Bạn đọc đang mượn cuốn sách này.")

    # Tạo bản ghi
    now = datetime.now().strftime("%d/%m/%Y")
    new_record = TrackBook(
        ma_ban_doc=ma_ban_doc,
        chuc_vu=chuc_vu,
        ma_sach=ma_sach,
        ten_sach=book.ten_sach,
        ngay_muon=now,
        ngay_tra="",
        trang_thai="Đang mượn"
    )
    data_handler.tracking_records.append(new_record)
    data_handler.save_data()
    return new_record

# TRẢ SÁCH 
def return_book(ma_ban_doc, ma_sach):
    """
    Xử lý trả sách.
    Raise ValueError nếu không tìm thấy bản ghi phù hợp.
    Trả về TrackBook đã cập nhật.
    """
    ma_ban_doc = str(ma_ban_doc).strip()
    ma_sach    = str(ma_sach).strip()

    record = next(
        (r for r in data_handler.tracking_records
         if r.ma_ban_doc == ma_ban_doc
         and r.ma_sach == ma_sach
         and r.trang_thai in ("Đang mượn", "Quá hạn")),
        None
    )

    record.ngay_tra   = datetime.now().strftime("%d/%m/%Y")
    record.trang_thai = "Đã trả"
    data_handler.save_data()
    return record

# THỐNG KÊ QUÁ HẠN & TIỀN PHẠT 
def get_overdue_records(ma_ban_doc=None):
    """
    Lấy danh sách bản ghi quá hạn, kèm số ngày quá hạn và tiền phạt.
    Lọc theo ma_ban_doc nếu truyền vào.
    Trả về list[dict] với các key:
        record, ten_ban_doc, so_ngay_qua_han, tien_phat
    """
    today = date.today()
    results = []

    if ma_ban_doc:
        reader = data_handler.readers_db.get(ma_ban_doc)
        if reader is None:
            raise ValueError(
                f"Bạn đọc {ma_ban_doc} không tồn tại trong hệ thống!"
            )

    for r in data_handler.tracking_records:
        if r.trang_thai != "Quá hạn":
            continue
        if ma_ban_doc and r.ma_ban_doc != ma_ban_doc:
            continue
        reader = data_handler.readers_db.get(r.ma_ban_doc)
        ten_bd = reader.ho_ten if reader else ""
        chuc_vu = reader.chuc_vu if reader else ""
        
        if chuc_vu == "Giảng viên":
            try:
                ngay_muon = datetime.strptime(r.ngay_muon, "%d/%m/%Y").date()
                so_ngay   = max((today - ngay_muon).days - 90, 0)
            except ValueError:
                so_ngay = 0
        if (chuc_vu == "Sinh viên" or chuc_vu == "Khác"):
            try:
                ngay_muon = datetime.strptime(r.ngay_muon, "%d/%m/%Y").date()
                so_ngay   = max((today - ngay_muon).days - 30, 0)
            except ValueError:
                so_ngay = 0         
        
        bang_muc_phat = {"Sinh viên": 2000, "Giảng viên": 3000, "Khác": 5000}
        muc_phat = bang_muc_phat.get(chuc_vu)
        tien_phat = (so_ngay / 7) * muc_phat

        results.append({
            "record":          r,
            "ten_ban_doc":     ten_bd,
            "chuc_vu":         chuc_vu,
            "so_ngay_qua_han": so_ngay,
            "muc_phat":        muc_phat,
            "tien_phat":       tien_phat,
        })
    if ma_ban_doc and len(results) == 0:
        raise ValueError(
            f"Bạn đọc {ma_ban_doc} không có sách quá hạn!"
        )
    return results

def get_borrow_history(keyword=None):
    """
    Lấy lịch sử mượn/trả. Lọc theo mã bạn đọc hoặc mã sách nếu có keyword.
    Trả về list[dict] với các key: record, ten_ban_doc
    """
    results = []
    for r in data_handler.tracking_records:
        if keyword and r.ma_ban_doc != keyword and r.ma_sach != keyword:
            continue
        reader = data_handler.readers_db.get(r.ma_ban_doc)
        ten_bd = reader.ho_ten if reader else ""
        results.append({"record": r, "ten_ban_doc": ten_bd})
    return results


def get_top_borrowed_books(top_n=5):
    """
    Thống kê số lượt mượn của từng sách (tính trên toàn bộ lịch sử mượn/trả,
    không phân biệt trạng thái), lấy ra top_n sách được mượn nhiều nhất.
    Trả về list[dict] với các key: ma_sach, ten_sach, so_lan_muon
    Sắp xếp giảm dần theo số lượt mượn; nếu số lượt mượn bằng nhau
    thì sắp theo mã sách tăng dần.
    """
    so_lan_muon = {}
    ten_sach_map = {}

    for r in data_handler.tracking_records:
        ma_sach = r.ma_sach
        so_lan_muon[ma_sach] = so_lan_muon.get(ma_sach, 0) + 1
        ten_sach_map[ma_sach] = r.ten_sach

    results = [
        {"ma_sach": ma_sach, "ten_sach": ten_sach_map[ma_sach], "so_lan_muon": count}
        for ma_sach, count in so_lan_muon.items()
    ]
    results.sort(key=lambda x: (-x["so_lan_muon"], x["ma_sach"]))

    if top_n is not None:
        results = results[:top_n]
    return results


def get_active_borrows(ma_ban_doc):
    """
    Lấy danh sách sách đang mượn (Đang mượn / Quá hạn) của một bạn đọc.
    Trả về list[TrackBook].
    """
    return [
        r for r in data_handler.tracking_records
        if r.ma_ban_doc == ma_ban_doc
        and r.trang_thai in ("Đang mượn", "Quá hạn")
    ]