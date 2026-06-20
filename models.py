class Book:
    def __init__(self, ma_sach, ten_sach, tac_gia, 
                 the_loai, so_luong_sach, tinh_trang_sach, 
                 nha_xuat_ban, nam_xuat_ban):
        self.ma_sach = str(ma_sach)
        self.ten_sach = ten_sach
        self.tac_gia = tac_gia
        self.the_loai = the_loai
        self.so_luong_sach = int(so_luong_sach)
        self.tinh_trang_sach = tinh_trang_sach
        self.nha_xuat_ban = nha_xuat_ban
        self.nam_xuat_ban = nam_xuat_ban
    def __str__(self):
        return (f"Mã sách: {self.ma_sach},Tên sách: {self.ten_sach},Tác giả: {self.tac_gia},"
                f"Số lượng sách: {self.so_luong_sach},Tình trạng sách: {self.tinh_trang_sach},"
                f"Nhà xuất bản: {self.nha_xuat_ban}, Năm xuất bản: {self.nam_xuat_ban}")

    def to_dict(self):
        data = self.__dict__.copy()
        data['ma_sach'] = str(self.ma_sach)
        return data

    @classmethod
    def from_dict(cls, data_dict):
        data_copy = data_dict.copy()
        if 'ma_sach' in data_copy:
            data_copy['ma_sach'] = str(data_copy['ma_sach'])
        return cls(**data_copy)

class Reader:
    def __init__(self, ma_ban_doc, ho_ten, ngay_sinh, gioi_tinh, dia_chi, chuc_vu, 
                 so_dien_thoai):
        self.ma_ban_doc = ma_ban_doc
        self.ho_ten = ho_ten
        self.ngay_sinh = ngay_sinh
        self.gioi_tinh = gioi_tinh
        self.dia_chi = dia_chi
        self.chuc_vu = chuc_vu
        self.so_dien_thoai = so_dien_thoai

    def __str__(self):
        return (f"Mã bạn đọc: {self.ma_ban_doc}, Họ tên: {self.ho_ten},"
                f"Ngày sinh: {self.ngay_sinh}, Giới tính: {self.gioi_tinh},"
                f"Địa chỉ: {self.dia_chi},Chức vụ : {self.chuc_vu},"
                f"Số điện thoại: {self.so_dien_thoai}")

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data_dict):
        return cls(**data_dict)

class TrackBook:
    def __init__(self, ma_ban_doc, chuc_vu, ma_sach, ten_sach, ngay_muon, 
                 ngay_tra, trang_thai):
        self.ma_ban_doc = ma_ban_doc
        self.chuc_vu = chuc_vu
        self.ma_sach = ma_sach
        self.ten_sach = ten_sach
        self.ngay_muon = ngay_muon
        self.ngay_tra = ngay_tra
        self.trang_thai = trang_thai

    def __str__(self):
        return (f"Mã bạn đọc: {self.ma_ban_doc}, Chức vụ: {self.chuc_vu},"
                f" Mã sách: {self.ma_sach},"
                f"Tên sách: {self.ten_sach}, Ngày mượn: {self.ngay_muon}, "
                f"Ngày trả: {self.ngay_tra}, Trạng thái: {self.trang_thai}]")

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data_dict):
        return cls(**data_dict)
    
    