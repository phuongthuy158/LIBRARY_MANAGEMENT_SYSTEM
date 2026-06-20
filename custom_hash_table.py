# custom_hash_table.py

class HashTable:
    def __init__(self, size=100): # Kích thước mặc định của bảng băm
        self.size = size
        self.table = [[] for _ in range(self.size)] # Tạo các bucket rỗng (danh sách)

    def _hash_function(self, key):
        """
        Chuyển key (string) thành một chỉ số trong bảng.
        """
        h = 8 # Khởi tạo giá trị bảng băm
        for char_val in str(key).encode('utf-8'): # Đảm bảo key là string và xử lý bytes
            h = (h * 31 + char_val) % self.size
        return h #Trả về chỉ số của bucket trong bảng băm

    def __setitem__(self, key, value):
        """
        Thêm hoặc cập nhật một cặp key-value.
        Sử dụng cú pháp: ht[key] = value
        """
        hashed_key = self._hash_function(key)
        bucket = self.table[hashed_key]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value) # Cập nhật nếu key đã tồn tại
                return
        bucket.append((key, value)) # Thêm mới nếu key chưa tồn tại

    def __getitem__(self, key):
        """
        Lấy giá trị dựa trên key.
        Sử dụng cú pháp: value = ht[key]
        """
        hashed_key = self._hash_function(key)
        bucket = self.table[hashed_key]

        for k, v in bucket:
            if k == key:
                return v
        raise KeyError(f"Key '{key}' not found in HashTable.")

    def __delitem__(self, key):
        """
        Xóa một cặp key-value.
        Sử dụng cú pháp: del ht[key]
        """
        hashed_key = self._hash_function(key)
        bucket = self.table[hashed_key]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                return
        raise KeyError(f"Key '{key}' not found in HashTable.")

    def __contains__(self, key):
        """
        Kiểm tra xem key có tồn tại trong bảng băm không.
        Sử dụng cú pháp: if key in ht:
        """
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __len__(self):
        """
        Trả về số lượng phần tử trong bảng băm.
        Sử dụng cú pháp: len(ht)
        """
        count = 0
        for bucket in self.table:
            count += len(bucket)
        return count

    def items(self):
        """
        Trả về một generator cho các cặp (key, value).
        Tương tự như dict.items().
        """
        for bucket in self.table:
            for key, value in bucket:
                yield key, value
    
    def values(self):
        """
        Trả về một generator cho các giá trị (value).
        Tương tự như dict.values().
        """
        for bucket in self.table:
            for _, value in bucket:
                yield value
    
    def keys(self):
        """
        Trả về một generator cho các khóa (key).
        Tương tự như dict.keys().
        """
        for bucket in self.table:
            for key, _ in bucket:
                yield key

    def clear(self):
        """
        Xóa tất cả các phần tử khỏi bảng băm.
        """
        self.table = [[] for _ in range(self.size)]

    def get(self, key, default=None):
        """
        Lấy giá trị dựa trên key.
        Trả về default nếu key không tồn tại.
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
        