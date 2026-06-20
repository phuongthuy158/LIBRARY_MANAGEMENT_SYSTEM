# data_handler.py
import json
from models import Book, Reader, TrackBook
from custom_hash_table import HashTable # << THAY ĐỔI Ở ĐÂY
from logger import logger

# Khởi tạo bằng HashTable thay vì dict
Hash_Table_Default_Size = 100 # Bạn có thể điều chỉnh kích thước này
books_db = HashTable(size=Hash_Table_Default_Size)
readers_db = HashTable(size=Hash_Table_Default_Size)
tracking_records = [] # Danh sách này có thể giữ nguyên vì không yêu cầu băm cụ thể

# File names for data persistence
BOOKS_FILE = "data/books.json"
READERS_FILE = "data/readers.json"
TRACKING_FILE = "data/tracking.json"

def save_data():
    global books_db, readers_db, tracking_records
    try:
        # Chuyển HashTable thành dict để serialize JSON
        books_to_save = {key: book.to_dict() for key, book in books_db.items()}
        logger.debug(f"Dữ liệu sách được lưu: {books_to_save}")
        with open(BOOKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(books_to_save, f, indent=4, ensure_ascii=False)

        readers_to_save = {key: reader.to_dict() for key, reader in readers_db.items()}
        logger.debug(f"Dữ liệu bạn đọc được lưu: {readers_to_save}")
        with open(READERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(readers_to_save, f, indent=4, ensure_ascii=False)
        
        tracking_to_save = [record.to_dict() for record in tracking_records]
        logger.debug(f"Dữ liệu mượn/trả được lưu: {tracking_to_save}")
        with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
            json.dump(tracking_to_save, f, indent=4, ensure_ascii=False)
        print("Du lieu da duoc luu.")
    except IOError as e:
        print(f"Loi khi luu du lieu: {e}")

def load_data():
    global books_db, readers_db, tracking_records
    
    books_db.clear() # Xóa dữ liệu cũ trước khi tải
    try:
        with open(BOOKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for ma_sach, book_data in data.items():
                logger.debug(f"Tải sách: {ma_sach} -> {book_data}")
                books_db[ma_sach] = Book.from_dict(book_data) # Sử dụng __setitem__
                logger.debug(f"Đã thêm sách vào books_db: {ma_sach}")
            for key, value in books_db.items():
                logger.debug(f"Key: {key}, Value: {value}")
    except FileNotFoundError:
        print(f"File {BOOKS_FILE} khong tim thay, bat dau voi du lieu trong.")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Loi khi tai {BOOKS_FILE}: {e}")

    readers_db.clear() # Xóa dữ liệu cũ trước khi tải
    try:
        with open(READERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for ma_bd, reader_data in data.items():
                readers_db[ma_bd] = Reader.from_dict(reader_data) # Sử dụng __setitem__
    except FileNotFoundError:
        print(f"File {READERS_FILE} khong tim thay, bat dau voi du lieu trong.")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Loi khi tai {READERS_FILE}: {e}")

    # tracking_records là list nên không cần clear kiểu HashTable
    global tracking_records # Đảm bảo ta gán lại cho biến global
    try:
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tracking_records = [TrackBook.from_dict(record_data) for record_data in data]
    except FileNotFoundError:
        print(f"File {TRACKING_FILE} khong tim thay, bat dau voi du lieu trong.")
        tracking_records = []
    except (IOError, json.JSONDecodeError) as e:
        print(f"Loi khi tai {TRACKING_FILE}: {e}")
        tracking_records = []