import json
import random
from faker import Faker

fake = Faker('vi_VN')

def generate_books(n):
    books = {}
    for i in range(1, n + 1):
        books[str(i)] = {
            "ma_sach": str(i),
            "ten_sach": fake.sentence(nb_words=4),
            "tac_gia": fake.name(),
            "the_loai": random.choice([
                "Tiểu thuyết", "Văn học", "Lịch sử", "Khoa học công nghệ", "Kỹ năng sống", "Giáo trình", "Tham khảo"]),
            "so_luong_sach": random.randint(1, 20),
            "tinh_trang_sach": random.choice(["Mới", "Đã sử dụng"]),
            "nha_xuat_ban": random.choice([
                "NXB Giáo dục Việt Nam", "NXB Trẻ", "NXB Kim Đồng", "NXB Văn Học", "NXB Lao Động",
                "NXB Tổng hợp TP.HCM", "NXB Khoa học và Kỹ thuật", "NXB Chính trị Quốc gia", "NXB Thanh Niên","NXB Phụ Nữ"]),
            "nam_xuat_ban": random.randint(1950, 2025)
        }
    return books

def generate_readers(n):
    readers = {}
    for i in range(1, n + 1):
        readers[str(i)] = {
            "ma_ban_doc": str(i),
            "ho_ten": fake.name(),
            "ngay_sinh": fake.date_of_birth(minimum_age=10, maximum_age=70).strftime("%d/%m/%Y"),
            "gioi_tinh": random.choice(["Nam", "Nữ", "Khác"]),
            "dia_chi": fake.city(),
            "chuc_vu": random.choice(["Giảng viên", "Sinh viên", "Khác"]),
            "so_dien_thoai": "0" + ''.join(random.choices('0123456789', k=9))
        }
    return readers

def generate_tracking_records(n, books, readers):
    tracking_records = []
    for i in range(1, n + 1):
        book_id = random.choice(list(books.keys()))
        reader_id = random.choice(list(readers.keys()))
        tracking_records.append({
            "ma_ban_doc": reader_id,
            "chuc_vu": readers[reader_id]["chuc_vu"],
            "ma_sach": book_id,
            "ten_sach": books[book_id]["ten_sach"],
            "ngay_muon": fake.date_between(start_date="-30d", end_date="today").strftime("%d/%m/%Y"),
            "ngay_tra": None,
            "trang_thai": random.choice(["Đang mượn", "Quá hạn"])
        })
    return tracking_records

if __name__ == "__main__":
    books = generate_books(10000)
    readers = generate_readers(5000)
    tracking_records = generate_tracking_records(30, books, readers)

    with open("data/books.json", "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    with open("data/readers.json", "w", encoding="utf-8") as f:
        json.dump(readers, f, ensure_ascii=False, indent=2)

    with open("data/tracking.json", "w", encoding="utf-8") as f:
        json.dump(tracking_records, f, ensure_ascii=False, indent=2)