from tkinter import messagebox
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import tkinter as tk
from tkinter import ttk
import data_handler
import book_manager
import reader_manager
import tracking_manager
from logger import logger
import customtkinter as ctk
from PIL import Image, ImageTk

_FONT_ENTRY = ("Arial Unicode MS", 11)
_FONT_LABEL = ("Arial Unicode MS", 10)
_FONT_BOLD  = ("Arial Unicode MS", 10, "bold")

# XÂY DỰNG GIAO DIỆN CHƯƠNG TRÌNH
class LibraryManagementSystem:
    # XÂY DỰNG TIÊU ĐỀ TRÊN CỦA CHƯƠNG TRÌNH
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Quản Lý Thư Viện")
        self.root.geometry("2000x950")

        self.style = ttk.Style()

        spacing_frame = ttk.Frame(root)
        spacing_frame.pack(pady=10)

        header_frame = ttk.Frame(root)
        header_frame.pack(fill="x")

        center_frame = ttk.Frame(header_frame)
        center_frame.pack(expand=True, fill="x")

        top_row = ttk.Frame(center_frame)
        top_row.pack(anchor="center", pady=(10, 0))

        try:
            logo_path = "hust.png"
            logo_image = Image.open(logo_path)
            desired_height = 70
            ratio = desired_height / logo_image.size[1]
            width = int(logo_image.size[0] * ratio)
            logo_image = logo_image.resize((width, desired_height),Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(top_row, image=logo_photo,bd=0)
            logo_label.image = logo_photo
            logo_label.pack(side=tk.LEFT, padx=(0, 15))

        except Exception as e:
            logger.error(f"Không thể tải logo: {e}")

        school_frame = tk.Frame(top_row)
        school_frame.pack(side=tk.LEFT)

        tk.Label(school_frame, text="ĐẠI HỌC BÁCH KHOA HÀ NỘI",
                font=("Arial Unicode MS", 18, "bold"), fg="#BE0000").pack(anchor="w")

        tk.Label(school_frame,text="HA NOI UNIVERSITY OF SCIENCE AND TECHNOLOGY",
                 font=("Arial Unicode MS", 11),fg="#BE0000").pack(anchor="w", fill='x')

        tk.Label(center_frame,text="HỆ THỐNG QUẢN LÝ THƯ VIỆN",
                 font=("Arial Unicode MS", 30, "bold"),fg="#BE0000"
                 ).pack(anchor="center", pady=(10, 15))

        # TẠO NOTEBOOK
        active_tab_bg = "white"
        active_tab_fg = "#003366"
        try:
            inactive_tab_bg = self.style.lookup('TButton', 'background') or "#E0EFFF"
            inactive_tab_fg = self.style.lookup('TButton', 'foreground') or "#495057"
            tab_hover_bg   = self.style.lookup('TButton', 'background', ('active',)) or "#C8E0FF"
        except tk.TclError:
            inactive_tab_bg, inactive_tab_fg, tab_hover_bg = "#F0F0F0", "#333333", "#E0E0E0"

        try:
            self.style.configure("TNotebook", borderwidth=0)
            self.style.configure("TNotebook.Client", background=active_tab_bg)
            self.style.configure("TNotebook.Tab",
                background=inactive_tab_bg, foreground=inactive_tab_fg,
                font=('Arial Unicode MS', 10), padding=[18, 6],
                relief="flat", borderwidth=0)
            self.style.map("TNotebook.Tab",
                background=[("selected", active_tab_bg), ("active", tab_hover_bg)],
                foreground=[("selected", active_tab_fg), ("active", active_tab_fg)],
                font=[("selected", ('Arial Unicode MS', 10, 'bold'))])
        except Exception as e:
            logger.error(f"Lỗi style Notebook: {e}")
            self.style.configure("TNotebook.Tab", padding=[18, 6], font=('Arial Unicode MS', 10))

        # TẠO TREEVIEW 
        self.style.configure("Treeview",
            background="#ffffff", fieldbackground="#ffffff", foreground="#333333",
            rowheight=30, font=('Arial Unicode MS', 10), borderwidth=0, relief="flat")
        self.style.configure("Treeview.Heading",
            font=('Arial Unicode MS', 11, 'bold'), background="#E9ECEF",
            foreground="#495057", relief="flat", borderwidth=0, padding=(5, 5))
        self.style.map('Treeview',
            background=[('selected', '#BBE2EC')],
            foreground=[('selected', '#1a365d')])

        # TẠO CÁC TAB CHỨC NĂNG CỦA CHƯƠNG TRÌNH
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=(5, 10))

        self.book_tab = ttk.Frame(self.notebook)
        self.reader_tab = ttk.Frame(self.notebook)
        self.tracking_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.book_tab, text=' QUẢN LÝ SÁCH ')
        self.notebook.add(self.reader_tab, text=' QUẢN LÝ BẠN ĐỌC ')
        self.notebook.add(self.tracking_tab, text=' MƯỢN/ TRẢ SÁCH ')

        self.setup_book_tab()
        self.setup_reader_tab()
        self.setup_tracking_tab()

        self.check_and_update_overdue_books()
        self.update_tracking_list()

    # XÂY DỰNG GIAO DIỆN TAB QUẢN LÝ SÁCH
    def setup_book_tab(self):
        btn_frame = ttk.Frame(self.book_tab)
        btn_frame.pack(pady=15, padx=20, fill='x')

        for text, color, cmd in [
            ("Thêm sách mới","#1F8949", self.show_add_book_window),
            ("Cập nhật thông tin sách","#166698", self.show_update_book_window),
            ("Tìm kiếm sách","#C7673A", self.show_search_book_window),
            ("Xóa sách","#B52C28", self.delete_book),
        ]:
            ctk.CTkButton(btn_frame, text=text, fg_color=color, corner_radius=5,
                          font=("Arial", 13, "bold"), text_color="white",
                          command=cmd).pack(side=tk.LEFT, padx=5)

        body = ttk.Frame(self.book_tab)
        body.pack(fill='both', expand=True, padx=10, pady=5)

        tree_frame = ttk.Frame(body)
        tree_frame.pack(side=tk.LEFT, fill='both', expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.book_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll.set,
            columns=("Mã sách", "Tên sách", "Thể loại", "Tác giả",
                     "Nhà xuất bản", "Năm XB", "Số lượng", "Còn lại", "Tình trạng"),
            show="headings"
        )
        tree_scroll.config(command=self.book_tree.yview)

        col_widths = {"Mã sách": 93, "Tên sách": 300, "Thể loại": 190,
                      "Tác giả": 170, "Nhà xuất bản": 230, "Năm XB": 100,
                      "Số lượng": 120, "Còn lại": 80, "Tình trạng": 160}
        for col, w in col_widths.items():
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=w, anchor="center")
        self.book_tree.column("Tên sách", anchor="w")
        self.book_tree.column("Tác giả", anchor="center")
        self.book_tree.pack(fill='both', expand=True)

        self.book_tree.tag_configure('oddrow', background="#DBEAFF")
        self.book_tree.tag_configure('evenrow', background='#FFFFFF')
        self.book_tree.tag_configure('overdue', background="#faa8ab")

        # XÂY DỰNG KHUNG CHỨC NĂNG SẮP XẾP SÁCH
        side = ttk.Frame(body, relief="groove")
        side.pack(side=tk.RIGHT, fill='y', padx=(10, 0), pady=0)

        sort_lf = ttk.LabelFrame(side, text="Sắp xếp sách theo danh sách", padding=8)
        sort_lf.pack(fill='x', padx=8, pady=8)

        self.book_sort_field = tk.StringVar(value="Mã sách")
        ttk.Combobox(sort_lf, textvariable=self.book_sort_field,
                     values=["Mã sách", "Tên sách", "Số lượng sách"],
                     state="readonly", width=10).pack(fill='x', pady=3)

        self.book_sort_order = tk.StringVar(value="Tăng dần")
        ord_f = ttk.Frame(sort_lf)
        ord_f.pack(fill='x', pady=3)
        ttk.Radiobutton(ord_f, text="Tăng dần", variable=self.book_sort_order, value="Tăng dần").pack(side=tk.LEFT)
        ttk.Radiobutton(ord_f, text="Giảm dần", variable=self.book_sort_order, value="Giảm dần").pack(side=tk.LEFT)

        ctk.CTkButton(sort_lf, text="Áp dụng", fg_color="#33b642", text_color="white",
                      corner_radius=5, command=self.update_book_list).pack(fill='x', pady=5)
        
        # XÂY DỰNG KHUNG CHỨC NĂNG LỌC DANH SÁCH
        filter_lf = ttk.LabelFrame(side, text="Lọc danh sách hiển thị sách", padding=8)
        filter_lf.pack(fill='x', padx=8, pady=8)

        ttk.Label(filter_lf, text="Thể loại:").pack(anchor="w")
        self.filter_the_loai = ttk.Combobox(filter_lf, state="readonly", width=22)
        self.filter_the_loai.pack(fill='x', pady=2)

        ttk.Label(filter_lf, text="Tác giả:").pack(anchor="w")
        self.filter_tac_gia = ttk.Combobox(filter_lf, state="readonly", width=22)
        self.filter_tac_gia.pack(fill='x', pady=2)

        ttk.Label(filter_lf, text="Nhà xuất bản:").pack(anchor="w")
        self.filter_nha_xuat_ban = ttk.Combobox(filter_lf, state="readonly", width=22)
        self.filter_nha_xuat_ban.pack(fill='x', pady=2)

        ttk.Label(filter_lf, text="Tình trạng sách:").pack(anchor="w")
        self.filter_tinh_trang_sach = ttk.Combobox(
            filter_lf, state="readonly", width=22,
            values=["Tất cả", "Sách mới", "Sách đã sử dụng"])
        self.filter_tinh_trang_sach.current(0)
        self.filter_tinh_trang_sach.pack(fill='x', pady=2)

        btn_row = ttk.Frame(filter_lf)
        btn_row.pack(fill='x', pady=5)
        ctk.CTkButton(btn_row, text="Áp dụng",  fg_color="#33b642", text_color="white",
                      corner_radius=5, command=self.apply_book_filter).pack(side=tk.LEFT, expand=True, fill='x', padx=2)
        ctk.CTkButton(btn_row, text="Hoàn tác", fg_color="#cead17", text_color="white",
                      corner_radius=5, command=self.undo_book_filter).pack(side=tk.LEFT, expand=True, fill='x', padx=2)

        self._refresh_book_filter_options()
        self.update_book_list()
        
    # XÂY DỰNG CÁC HÀM SẮP XẾP   
    @staticmethod
    def _viet_sort_key(text: str) -> list:
        VI_ORDER = {
            'a': 1,'ă': 2,'â': 3,'b': 4,'c': 5,'d': 6,'đ': 7,'e': 8,'ê': 9,'g': 10,'h': 11,
            'i': 12,'k': 13,'l': 14,'m': 15,'n': 16,'o': 17,'ô': 18,'ơ': 19,'p': 20,'q': 21,
            'r': 22,'s': 23,'t': 24,'u': 25,'ư': 26,'v': 27,'x': 28,'y': 29,}
        TONE_BASE = {
            'à':'a','á':'a','ả':'a','ã':'a','ạ':'a','ầ':'â','ấ':'â','ẩ':'â','ẫ':'â','ậ':'â',
            'ằ':'ă','ắ':'ă','ẳ':'ă','ẵ':'ă','ặ':'ă','è':'e','é':'e','ẻ':'e','ẽ':'e','ẹ':'e',
            'ề':'ê','ế':'ê','ể':'ê','ễ':'ê','ệ':'ê','ì':'i','í':'i','ỉ':'i','ĩ':'i','ị':'i',
            'ò':'o','ó':'o','ỏ':'o','õ':'o','ọ':'o','ồ':'ô','ố':'ô','ổ':'ô','ỗ':'ô','ộ':'ô',
            'ờ':'ơ','ớ':'ơ','ở':'ơ','ỡ':'ơ','ợ':'ơ','ù':'u','ú':'u','ủ':'u','ũ':'u','ụ':'u',
            'ừ':'ư','ứ':'ư','ử':'ư','ữ':'ư','ự':'ư','ỳ':'y','ý':'y','ỷ':'y','ỹ':'y','ỵ':'y',
            'd':'d','đ':'đ',}
        TONE_RANK = {
            'a':0,'á':1,'à':2,'ả':3,'ã':4,'ạ':5,'ă':0,'ắ':1,'ằ':2,'ẳ':3,'ẵ':4,'ặ':5,
            'â':0,'ấ':1,'ầ':2,'ẩ':3,'ẫ':4,'ậ':5,'e':0,'é':1,'è':2,'ẻ':3,'ẽ':4,'ẹ':5,
            'ê':0,'ế':1,'ề':2,'ể':3,'ễ':4,'ệ':5,'i':0,'í':1,'ì':2,'ỉ':3,'ĩ':4,'ị':5,
            'o':0,'ó':1,'ò':2,'ỏ':3,'õ':4,'ọ':5,'ô':0,'ố':1,'ồ':2,'ổ':3,'ỗ':4,'ộ':5,
            'ơ':0,'ớ':1,'ờ':2,'ở':3,'ỡ':4,'ợ':5,'u':0,'ú':1,'ù':2,'ủ':3,'ũ':4,'ụ':5,
            'ư':0,'ứ':1,'ừ':2,'ử':3,'ữ':4,'ự':5,'y':0,'ý':1,'ỳ':2,'ỷ':3,'ỹ':4,'ỵ':5,}
        result = []
        for ch in text.lower():
            base = TONE_BASE.get(ch, ch)
            base = base if base in VI_ORDER else ch
            primary = VI_ORDER.get(base, 99)
            tone    = TONE_RANK.get(ch, 0)
            result.append((primary, tone, ord(ch)))
        return result

    @staticmethod
    def _last_word_sort_key(ho_ten: str) -> list:
        """Sắp xếp theo tiếng cuối trong tên (chuẩn tiếng Việt)."""
        parts = ho_ten.strip().split()
        if not parts:
            return []
        last = parts[-1]
        rest = " ".join(parts[:-1])
        VI_ORDER = {
            'a': 1, 'ă': 2, 'â': 3, 'b': 4, 'c': 5, 'd': 6, 'đ': 7,
            'e': 8, 'ê': 9, 'g': 10, 'h': 11, 'i': 12, 'k': 13, 'l': 14,
            'm': 15, 'n': 16, 'o': 17, 'ô': 18, 'ơ': 19, 'p': 20, 'q': 21,
            'r': 22, 's': 23, 't': 24, 'u': 25, 'ư': 26, 'v': 27, 'x': 28, 'y': 29,}
        TONE_BASE = {
            'à':'a','á':'a','ả':'a','ã':'a','ạ':'a','ầ':'â','ấ':'â','ẩ':'â','ẫ':'â','ậ':'â',
            'ằ':'ă','ắ':'ă','ẳ':'ă','ẵ':'ă','ặ':'ă','è':'e','é':'e','ẻ':'e','ẽ':'e','ẹ':'e',
            'ề':'ê','ế':'ê','ể':'ê','ễ':'ê','ệ':'ê','ì':'i','í':'i','ỉ':'i','ĩ':'i','ị':'i',
            'ò':'o','ó':'o','ỏ':'o','õ':'o','ọ':'o','ồ':'ô','ố':'ô','ổ':'ô','ỗ':'ô','ộ':'ô',
            'ờ':'ơ','ớ':'ơ','ở':'ơ','ỡ':'ơ','ợ':'ơ','ù':'u','ú':'u','ủ':'u','ũ':'u','ụ':'u',
            'ừ':'ư','ứ':'ư','ử':'ư','ữ':'ư','ự':'ư','ỳ':'y','ý':'y','ỷ':'y','ỹ':'y','ỵ':'y',}
        def _char_key(ch):
            base = TONE_BASE.get(ch, ch)
            return (VI_ORDER.get(base, 99), ord(ch))
        last_key = [_char_key(c) for c in last.lower()]
        rest_key = [_char_key(c) for c in rest.lower()]
        return (last_key, rest_key)

    @staticmethod
    def _ma_sach_sort_key(ma: str):
        parts = []
        buf = ''
        is_digit_mode = None
        for ch in ma:
            is_digit = ch.isdigit()
            if is_digit_mode is None:
                is_digit_mode = is_digit
            if is_digit == is_digit_mode:
                buf += ch
            else:
                parts.append(int(buf) if is_digit_mode else buf.lower())
                buf = ch
                is_digit_mode = is_digit
        if buf:
            parts.append(int(buf) if is_digit_mode else buf.lower())
        return [(0, p) if isinstance(p, int) else (1, p) for p in parts]

    # CẬP NHẬT GIAO DIỆN THEO BỘ LỌC SẮP XẾP 
    def update_book_list(self, books=None):
        if books is None:
            books = list(data_handler.books_db.values())

        sort_choice = self.book_sort_field.get()
        reverse     = (self.book_sort_order.get() == "Giảm dần")

        if sort_choice == "Mã sách":
            books = sorted(books, key=lambda b: self._ma_sach_sort_key(b.ma_sach), reverse=reverse)
        elif sort_choice == "Tên sách":
            books = sorted(books, key=lambda b: self._viet_sort_key(b.ten_sach), reverse=reverse)
        elif sort_choice == "Số lượng sách":
            books = sorted(books, key=lambda b: int(b.so_luong_sach) if str(b.so_luong_sach).isdigit() else 0, reverse=reverse)
        else:
            books = sorted(books, key=lambda b: self._ma_sach_sort_key(b.ma_sach), reverse=reverse)

        self._fill_book_tree(books)
        self._refresh_book_filter_options()

    def _fill_book_tree(self, books):
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
        for i, b in enumerate(books):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            self.book_tree.insert("", "end", values=(
                b.ma_sach, b.ten_sach, b.the_loai, b.tac_gia,
                b.nha_xuat_ban, getattr(b, 'nam_xuat_ban', ''),
                b.so_luong_sach,
                tracking_manager.get_so_luong_con_lai(b.ma_sach),
                b.tinh_trang_sach
            ), tags=(tag,))
        self.book_tree.tag_configure('oddrow', background='#E8F4FA')
        self.book_tree.tag_configure('evenrow', background='#FFFFFF')

    @staticmethod
    def _find_book_key(raw_val) -> str | None:
        raw_str = str(raw_val)
        if raw_str in data_handler.books_db:
            return raw_str
        for k in data_handler.books_db:
            if str(k) == raw_str:
                return k
        return None
    
    # XÂY DỰNG BỘ LỌC
    def _refresh_book_filter_options(self):
        books = list(data_handler.books_db.values())
        the_loai = ["Tất cả"] + sorted({b.the_loai   for b in books if b.the_loai})
        tac_gia = ["Tất cả"] + sorted({b.tac_gia    for b in books if b.tac_gia})
        nha_xuat_ban = ["Tất cả"] + sorted({b.nha_xuat_ban for b in books if b.nha_xuat_ban})

        self.filter_the_loai["values"] = the_loai
        self.filter_tac_gia["values"] = tac_gia
        self.filter_nha_xuat_ban["values"] = nha_xuat_ban
        self.filter_tinh_trang_sach["values"] = ["Tất cả"] + sorted({b.tinh_trang_sach for b in books if b.tinh_trang_sach})

        for cb in (self.filter_the_loai, self.filter_tac_gia, self.filter_nha_xuat_ban, self.filter_tinh_trang_sach):
            if cb.get() not in cb["values"]:
                cb.current(0)

    def apply_book_filter(self):
        books = list(data_handler.books_db.values())
        the_loai = self.filter_the_loai.get()
        tac_gia = self.filter_tac_gia.get()
        nha_xuat_ban = self.filter_nha_xuat_ban.get()
        tinh_trang_sach = self.filter_tinh_trang_sach.get()

        if the_loai and the_loai!= "Tất cả": books = [b for b in books if b.the_loai == the_loai]
        if tac_gia and tac_gia!= "Tất cả": books = [b for b in books if b.tac_gia == tac_gia]
        if nha_xuat_ban and nha_xuat_ban!= "Tất cả": books = [b for b in books if b.nha_xuat_ban == nha_xuat_ban]
        if tinh_trang_sach and tinh_trang_sach!= "Tất cả": books = [b for b in books if b.tinh_trang_sach == tinh_trang_sach]

        self._fill_book_tree(books)
    
    # THAO TÁC HỦY BỎ BỘ LỌC
    def undo_book_filter(self):
        for cb in (self.filter_the_loai, self.filter_tac_gia, self.filter_nha_xuat_ban, self.filter_tinh_trang_sach):
            cb.current(0)
        self.update_book_list()
    
    # THAO TÁC THÊM SÁCH MỚI 
    def show_add_book_window(self):
        logger.info("Mở cửa sổ thêm sách mới")
        win = tk.Toplevel(self.root)
        win.title("Thêm Sách Mới")
        win.geometry("600x800")
        win.grab_set()

        ttk.Label(win, text="Thêm sách mới", font=("Arial Unicode MS", 14, "bold")).pack(pady=10)

        form = ttk.Frame(win)
        form.pack(fill='both', expand=True, padx=20)

        fields = {}
        for lbl, key in [("Mã sách", "ma_sach"), ("Tên sách", "ten_sach"),
                         ("Tác giả", "tac_gia"), ("Nhà xuất bản", "nha_xuat_ban"),
                         ("Năm xuất bản", "nam_xuat_ban"),
                         ("Số lượng", "so_luong_sach")]:
            ttk.Label(form, text=lbl + ":", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
            e = ttk.Entry(form, font=_FONT_ENTRY, width=50)
            e.pack(fill='x')
            fields[key] = e

        ttk.Label(form, text="Thể loại:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        genres_existing = sorted({b.the_loai for b in data_handler.books_db.values() if b.the_loai})
        the_loai_var = tk.StringVar(value="Tiểu thuyết")
        the_loai_cb  = ttk.Combobox(form, textvariable=the_loai_var, font=_FONT_ENTRY, state="readonly",
                                     values=genres_existing + ["-- Nhập thể loại mới --"], width=48)
        the_loai_cb.pack(fill='x')

        custom_lbl   = ttk.Label(form, text="Nhập thể loại mới:", font=_FONT_LABEL)
        custom_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)

        def on_genre_change(e=None):
            if the_loai_var.get() == "-- Nhập thể loại mới --":
                custom_lbl.pack(anchor="w", pady=(4, 0))
                custom_entry.pack(fill='x')
                custom_entry.focus_set()
            else:
                custom_lbl.pack_forget()
                custom_entry.pack_forget()
        the_loai_cb.bind("<<ComboboxSelected>>", on_genre_change)

        ttk.Label(form, text="Tình trạng sách:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        tinh_trang_sach_var = tk.StringVar(value="Sách mới")
        ttk.Combobox(form, textvariable=tinh_trang_sach_var,
                     values=["Sách mới", "Sách đã sử dụng"],
                     state="readonly", width=48, font=_FONT_ENTRY).pack(fill='x')

        def save_book():
            ma_sach       = fields["ma_sach"].get().strip()
            ten_sach      = fields["ten_sach"].get().strip()
            tac_gia       = fields["tac_gia"].get().strip()
            nha_xuat_ban  = fields["nha_xuat_ban"].get().strip()
            nam_xuat_ban  = fields["nam_xuat_ban"].get().strip()
            so_luong_sach = fields["so_luong_sach"].get().strip()
            the_loai      = (custom_entry.get().strip()
                             if the_loai_var.get() == "-- Nhập thể loại mới --"
                             else the_loai_var.get().strip())
            tinh_trang_sach = tinh_trang_sach_var.get().strip()

            try:
                book_manager.add_book(
                    ma_sach, ten_sach, tac_gia, the_loai,
                    so_luong_sach, tinh_trang_sach, nha_xuat_ban, nam_xuat_ban
                )
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e), parent=win)
                return

            self.update_book_list()
            logger.info(f"Thêm sách: {ma_sach}")
            messagebox.showinfo("Thông báo", f"Đã thêm sách {ten_sach} thành công", parent=win)
            win.destroy()

        ttk.Button(win, text="Lưu", command=save_book, bootstyle="success").pack(pady=15, fill='x', padx=20)

    # THAO TÁC CẬP NHẬT SÁCH 
    def show_update_book_window(self):
        logger.info("Mở cửa sổ cập nhật sách")
        if not self.book_tree.selection():
            messagebox.showwarning("Thông báo", "Vui lòng chọn một cuốn sách để cập nhật thông tin")
            return

        selected = self.book_tree.selection()[0]
        ma_sach  = str(self.book_tree.item(selected)['values'][0])

        if ma_sach not in data_handler.books_db:
            messagebox.showerror("Lỗi", f"Mã sách '{ma_sach}' không tồn tại!")
            return

        book = data_handler.books_db[ma_sach]
        win  = tk.Toplevel(self.root)
        win.title("Cập Nhật Thông Tin Sách")
        win.geometry("600x800")
        win.grab_set()

        ttk.Label(win, text="Cập nhật thông tin sách", font=("Arial Unicode MS", 14, "bold")).pack(pady=10)
        ttk.Label(win, text=f"Mã sách: {ma_sach}  (không thể thay đổi)",
                  font=_FONT_BOLD, foreground="#c0392b").pack(pady=3)

        form = ttk.Frame(win)
        form.pack(fill='both', expand=True, padx=20)

        fields = {}
        for lbl, key, val in [
            ("Tên sách", "ten_sach", book.ten_sach),
            ("Tác giả", "tac_gia", book.tac_gia),
            ("Nhà xuất bản", "nha_xuat_ban", book.nha_xuat_ban),
            ("Năm xuất bản", "nam_xuat_ban", getattr(book, 'nam_xuat_ban', '')),
            ("Số lượng", "so_luong_sach", str(book.so_luong_sach)),
        ]:
            ttk.Label(form, text=lbl + ":", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
            e = ttk.Entry(form, font=_FONT_ENTRY, width=50)
            e.insert(0, val)
            e.pack(fill='x')
            fields[key] = e

        ttk.Label(form, text="Thể loại:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        genres_existing = sorted({b.the_loai for b in data_handler.books_db.values() if b.the_loai})
        the_loai_var = tk.StringVar(value=book.the_loai)
        the_loai_cb  = ttk.Combobox(form, textvariable=the_loai_var, font=_FONT_ENTRY, state="readonly",
                                     values=genres_existing + ["-- Nhập thể loại mới --"], width=48)
        the_loai_cb.pack(fill='x')
        custom_lbl   = ttk.Label(form, text="Nhập thể loại mới:", font=_FONT_LABEL)
        custom_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)

        def on_genre_change(e=None):
            if the_loai_var.get() == "-- Nhập thể loại mới --":
                custom_lbl.pack(anchor="w", pady=(4, 0))
                custom_entry.pack(fill='x')
                custom_entry.focus_set()
            else:
                custom_lbl.pack_forget(); custom_entry.pack_forget()
        the_loai_cb.bind("<<ComboboxSelected>>", on_genre_change)

        ttk.Label(form, text="Tình trạng sách:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        tinh_trang_sach_var = tk.StringVar(value=book.tinh_trang_sach)
        ttk.Combobox(form, textvariable=tinh_trang_sach_var,
                     values=["Sách mới", "Sách đã sử dụng"],
                     state="readonly", width=48, font=_FONT_ENTRY).pack(fill='x')

        def update_book():
            ten_sach = fields["ten_sach"].get().strip()
            tac_gia = fields["tac_gia"].get().strip()
            nha_xuat_ban = fields["nha_xuat_ban"].get().strip()
            nam_xuat_ban = fields["nam_xuat_ban"].get().strip()
            so_luong_sach = fields["so_luong_sach"].get().strip()
            the_loai = (custom_entry.get().strip()
                             if the_loai_var.get() == "-- Nhập thể loại mới --"
                             else the_loai_var.get().strip())
            tinh_trang_sach = tinh_trang_sach_var.get().strip()

            if not all([ten_sach, the_loai, tac_gia, so_luong_sach, tinh_trang_sach]):
                messagebox.showerror("Lỗi", "Các thông tin bắt buộc không được phép để trống", parent=win)
                return
            if not so_luong_sach.isdigit():
                messagebox.showerror("Lỗi", "Số lượng sách không hợp lệ.", parent=win)
                return

            try:
                book_manager.update_book(
                    ma_sach, ten_sach, tac_gia, the_loai,
                    so_luong_sach, tinh_trang_sach, nha_xuat_ban, nam_xuat_ban
                )
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e), parent=win)
                return

            self.update_book_list()
            self.update_tracking_list()
            logger.info(f"Cập nhật sách: {ma_sach}")

            messagebox.showinfo("Thông báo", f"Cập nhật thông tin sách '{ten_sach}' thành công!", parent=win)
            win.destroy()

        ttk.Button(win, text="Lưu", command=update_book, bootstyle="success").pack(pady=15, fill='x', padx=20)

    # THAO TÁC TÌM KIẾM SÁCH 
    def show_search_book_window(self):
        logger.info("Mở cửa sổ tìm kiếm sách")
        win = tk.Toplevel(self.root)
        win.title("Tìm Kiếm Sách")
        win.geometry("1100x520")
        win.grab_set()

        top = ttk.Frame(win)
        top.pack(fill='x', padx=15, pady=12)

        ttk.Label(top, text="Tìm theo:", font=_FONT_LABEL).pack(side=tk.LEFT)
        search_field_var = tk.StringVar(value="Tên sách")
        field_cb = ttk.Combobox(top, textvariable=search_field_var,
                                 values=["Mã sách", "Tên sách", "Thể loại", "Tác giả", "Nhà xuất bản"],
                                 state="readonly", width=16, font=_FONT_ENTRY)
        field_cb.pack(side=tk.LEFT, padx=(4, 12))

        ttk.Label(top, text="Từ khóa:", font=_FONT_LABEL).pack(side=tk.LEFT)
        search_var = tk.StringVar()
        entry = ttk.Entry(top, font=_FONT_ENTRY, textvariable=search_var, width=30)
        entry.pack(side=tk.LEFT, padx=8)
        entry.focus()

        cols = ("Mã sách", "Tên sách", "Thể loại", "Tác giả", "Nhà xuất bản",
                "Năm xuất bản", "Số lượng sách", "Số còn lại", "Tình trạng sách")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100, anchor="center")
        tree.column("Tên sách",  width=200, anchor="w")
        tree.column("Tác giả",   width=130, anchor="w")
        tree.pack(fill='both', expand=True, padx=15, pady=5)

        def do_search(event=None):
            kw    = search_var.get().strip()
            field = search_field_var.get()

            field_map = {
                "Mã sách": "ma_sach",
                "Tên sách": "ten_sach",
                "Thể loại": "the_loai",
                "Tác giả": "tac_gia",
                "Nhà xuất bản": "nha_xuat_ban",
            }
            found = book_manager.search_books(kw, field_map.get(field, "ten_sach"))

            for item in tree.get_children():
                tree.delete(item)
            for b in found:
                tree.insert("", "end", values=(
                    b.ma_sach, b.ten_sach, b.the_loai, b.tac_gia,
                    b.nha_xuat_ban, getattr(b, 'nam_xuat_ban', ''),
                    b.so_luong_sach,
                    tracking_manager.get_so_luong_con_lai(b.ma_sach),
                    b.tinh_trang_sach))

            if found:
                messagebox.showinfo("Thông báo", f"Tìm thấy {len(found)} cuốn sách thỏa mãn yêu cầu.", parent=win)
            else:
                messagebox.showinfo("Thông báo", "Không tìm thấy cuốn sách nào thỏa mãn yêu cầu.", parent=win)

        entry.bind("<Return>", do_search)
        ttk.Button(top, text="Tìm kiếm", command=do_search, bootstyle="warning").pack(side=tk.LEFT, padx=8)

    # THAO TÁC XÓA SÁCH 
    def delete_book(self):
        if not self.book_tree.selection():
            messagebox.showwarning("Thông báo", "Vui lòng chọn một cuốn sách để xóa")
            return

        selected  = self.book_tree.selection()[0]
        raw_val   = self.book_tree.item(selected)['values'][0]
        ma_sach   = self._find_book_key(raw_val)

        if ma_sach is None:
            messagebox.showerror("Lỗi", f"Không tìm thấy mã sách '{raw_val}' trong cơ sở dữ liệu!")
            return

        dang_muon = [r for r in data_handler.tracking_records
                     if str(r.ma_sach) == str(ma_sach) and r.trang_thai in ("Đang mượn", "Quá hạn")]
        if dang_muon:
            messagebox.showerror("Thông báo", "Không thể xóa sách đang được mượn")
            return

        if not messagebox.askyesno("Xác nhận",
                f"Bạn có chắc chắn muốn xóa sách có mã sách {ma_sach} hay không?"):
            return

        try:
            book_manager.delete_book(ma_sach)
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
            return

        self.update_book_list()
        messagebox.showinfo("Thông báo", "Đã xóa sách thành công!")

    # XÂY DỰNG TAB CHỨC NĂNG QUẢN LÝ BẠN ĐỌC
    def setup_reader_tab(self):
        btn_frame = ttk.Frame(self.reader_tab)
        btn_frame.pack(pady=15, padx=20, fill='x')

        for text, color, cmd in [
            ("Thêm bạn đọc mới","#1F8949", self.show_add_reader_window),
            ("Cập nhật thông tin bạn đọc","#166698", self.show_update_reader_window),
            ("Tìm kiếm thông tin bạn đọc","#C7673A", self.show_search_reader_window),
            ("Xóa bạn đọc","#B52C28", self.delete_reader),
        ]:
            ctk.CTkButton(btn_frame, text=text, fg_color=color, corner_radius=5,
                          font=("Segoe UI", 13, "bold"), text_color="white",
                          command=cmd).pack(side=tk.LEFT, padx=5)

        body = ttk.Frame(self.reader_tab)
        body.pack(fill='both', expand=True, padx=10, pady=5)

        tree_frame = ttk.Frame(body)
        tree_frame.pack(side=tk.LEFT, fill='both', expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.reader_tree = ttk.Treeview(
            tree_frame,
            columns=('Mã bạn đọc', 'Họ tên', 'Ngày sinh', 'Giới tính', 'Địa chỉ', 'Chức vụ', 'Số điện thoại'),
            yscrollcommand=tree_scroll.set,
            show="headings"
        )
        tree_scroll.config(command=self.reader_tree.yview)

        col_w = {'Mã bạn đọc': 90, 'Họ tên': 200, 'Ngày sinh': 110,
                 'Giới tính': 90, 'Địa chỉ': 150, 'Chức vụ': 100, 'Số điện thoại': 130}
        for col, w in col_w.items():
            self.reader_tree.heading(col, text=col)
            self.reader_tree.column(col, width=w, anchor="center")
        self.reader_tree.column('Họ tên', anchor="w")
        self.reader_tree.column('Địa chỉ',   anchor="center")
        self.reader_tree.column('Chức vụ',   anchor="center")
        self.reader_tree.pack(fill='both', expand=True)
        self.reader_tree.tag_configure('oddrow',  background='#E8F4FA')
        self.reader_tree.tag_configure('evenrow', background='#FFFFFF')

        # XÂY DỰNG KHUNG CHỨC NĂNG SẮP XẾP BẠN ĐỌC
        side = ttk.Frame(body, relief="groove")
        side.pack(side=tk.RIGHT, fill='y', padx=(10, 0))

        sort_lf = ttk.LabelFrame(side, text="Sắp xếp bạn đọc theo danh sách", padding=8)
        sort_lf.pack(fill='x', padx=8, pady=8)

        self.reader_sort_field = tk.StringVar(value="Mã bạn đọc")
        ttk.Combobox(sort_lf, textvariable=self.reader_sort_field,
                     values=["Mã bạn đọc", "Tên bạn đọc"],
                     state="readonly", width=22).pack(fill='x', pady=3)

        self.reader_sort_order = tk.StringVar(value="Tăng dần")
        ord_f = ttk.Frame(sort_lf)
        ord_f.pack(fill='x', pady=3)
        ttk.Radiobutton(ord_f, text="Tăng dần", variable=self.reader_sort_order, value="Tăng dần").pack(side=tk.LEFT)
        ttk.Radiobutton(ord_f, text="Giảm dần", variable=self.reader_sort_order, value="Giảm dần").pack(side=tk.LEFT)

        ctk.CTkButton(sort_lf, text="Áp dụng", fg_color="#33b642", text_color="white",
                      corner_radius=5, command=self.update_reader_list).pack(fill='x', pady=5)

        # XÂY DỰNG KHUNG CHỨC NĂNG LỌC DANH SÁCH BẠN ĐỌC
        filter_lf = ttk.LabelFrame(side, text="Lọc danh sách hiển thị bạn đọc", padding=8)
        filter_lf.pack(fill='x', padx=8, pady=8)

        ttk.Label(filter_lf, text="Giới tính:").pack(anchor="w")
        self.filter_by_gioi_tinh = ttk.Combobox(filter_lf, state="readonly", width=22,
                                              values=["Tất cả", "Nam", "Nữ", "Khác"])
        self.filter_by_gioi_tinh.current(0)
        self.filter_by_gioi_tinh.pack(fill='x', pady=2)

        ttk.Label(filter_lf, text="Địa chỉ:").pack(anchor="w")
        self.filter_by_dia_chi = ttk.Combobox(filter_lf, state="readonly", width=22)
        self.filter_by_dia_chi.pack(fill='x', pady=2)

        ttk.Label(filter_lf, text="Chức vụ:").pack(anchor="w")
        self.filter_by_chuc_vu = ttk.Combobox(filter_lf, state="readonly", width=22,
                                              values=["Tất cả", "Giảng viên", "Sinh viên", "Khác"])
        self.filter_by_chuc_vu.current(0)
        self.filter_by_chuc_vu.pack(fill='x', pady=2)

        btn_row = ttk.Frame(filter_lf)
        btn_row.pack(fill='x', pady=5)
        ctk.CTkButton(btn_row, text="Áp dụng",  fg_color="#33b642", text_color="white",
                      corner_radius=5, command=self.apply_reader_filter).pack(side=tk.LEFT, expand=True, fill='x', padx=2)
        ctk.CTkButton(btn_row, text="Hoàn tác", fg_color="#cead17", text_color="white",
                      corner_radius=5, command=self.undo_reader_filter).pack(side=tk.LEFT, expand=True, fill='x', padx=2)

        self._refresh_reader_filter_options()
        self.update_reader_list()

    def _refresh_reader_filter_options(self):
        addresses = ["Tất cả"] + sorted({r.dia_chi for r in data_handler.readers_db.values() if r.dia_chi})
        self.filter_by_dia_chi["values"] = addresses
        if self.filter_by_dia_chi.get() not in addresses:
            self.filter_by_dia_chi.current(0)

    def apply_reader_filter(self):
        readers = list(data_handler.readers_db.values())
        gioi_tinh  = self.filter_by_gioi_tinh.get()
        dia_chi = self.filter_by_dia_chi.get()
        chuc_vu = self.filter_by_chuc_vu.get()
        if gioi_tinh  and gioi_tinh  != "Tất cả": readers = [r for r in readers if r.gioi_tinh == gioi_tinh]
        if dia_chi and dia_chi != "Tất cả": readers = [r for r in readers if r.dia_chi   == dia_chi]
        if chuc_vu and chuc_vu != "Tất cả": readers = [r for r in readers if r.chuc_vu == chuc_vu]
        self._fill_reader_tree(readers)

    def update_reader_list(self, readers=None):
        if readers is None:
            readers = list(data_handler.readers_db.values())

        gioi_tinh = self.filter_by_gioi_tinh.get()
        dia_chi = self.filter_by_dia_chi.get()
        chuc_vu = self.filter_by_chuc_vu.get()
        if gioi_tinh and gioi_tinh!= "Tất cả": readers = [r for r in readers if r.gioi_tinh == gioi_tinh]
        if dia_chi and dia_chi!= "Tất cả": readers = [r for r in readers if r.dia_chi   == dia_chi]
        if chuc_vu and chuc_vu!= "Tất cả": readers = [r for r in readers if r.chuc_vu   == chuc_vu]

        reverse = (self.reader_sort_order.get() == "Giảm dần")
        sort_by = self.reader_sort_field.get()
        try:
            if sort_by == "Tên bạn đọc":
                readers.sort(key=lambda r: self._last_word_sort_key(
                    r.ho_ten if hasattr(r, 'ho_ten') else r.ten), reverse=reverse)
            else:
                readers.sort(key=lambda r: (int(r.ma_ban_doc) if r.ma_ban_doc.isdigit() else r.ma_ban_doc),
                             reverse=reverse)
        except Exception:
            pass

        self._fill_reader_tree(readers)
        self._refresh_reader_filter_options()

    def _fill_reader_tree(self, readers):
        for item in self.reader_tree.get_children():
            self.reader_tree.delete(item)
        for i, r in enumerate(readers):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            self.reader_tree.insert("", "end", values=(
                r.ma_ban_doc, r.ho_ten, r.ngay_sinh, r.gioi_tinh, r.dia_chi, r.chuc_vu, r.so_dien_thoai
            ), tags=(tag,))
        self.reader_tree.tag_configure('oddrow',  background='#E8F4FA')
        self.reader_tree.tag_configure('evenrow', background='#FFFFFF')

    # THAO TÁC HỦY BỎ BỘ LỌC
    def undo_reader_filter(self):
        self.filter_by_gioi_tinh.current(0)
        self.filter_by_dia_chi.current(0)
        self.filter_by_chuc_vu.current(0)
        self.update_reader_list()

    # THAO TÁC THÊM BẠN ĐỌC MỚI 
    def show_add_reader_window(self):
        logger.info("Mở cửa sổ thêm bạn đọc mới")
        win = tk.Toplevel(self.root)
        win.title("Thêm Bạn Đọc Mới")
        win.geometry("500x520")
        win.grab_set()

        ttk.Label(win, text="Thêm bạn đọc mới", font=("Arial Unicode MS", 14, "bold")).pack(pady=10)

        form = ScrolledFrame(win)
        form.pack(fill=tk.BOTH, expand=tk.YES, padx=20, pady=5)

        ttk.Label(form, text="Mã bạn đọc:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        ma_doc_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)
        ma_doc_entry.pack(fill='x')

        ttk.Label(form, text="Họ và tên:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        ho_ten_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)
        ho_ten_entry.pack(fill='x')

        ttk.Label(form, text="Ngày sinh (DD/MM/YYYY):", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        ngay_sinh_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)
        ngay_sinh_entry.pack(fill='x')

        ttk.Label(form, text="Giới tính:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        gioi_tinh_cb = ttk.Combobox(form, values=["Nam", "Nữ", "Khác"], state="readonly",
                                     width=48, font=_FONT_ENTRY)
        gioi_tinh_cb.current(0)
        gioi_tinh_cb.pack(fill='x')

        ttk.Label(form, text="Địa chỉ:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        dia_chi_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)
        dia_chi_entry.pack(fill='x')

        ttk.Label(form, text="Chức vụ:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        chuc_vu_cb = ttk.Combobox(form, values=["Giảng viên", "Sinh viên", "Khác"], state="readonly",
                                     width=48, font=_FONT_ENTRY)
        chuc_vu_cb.current(0)
        chuc_vu_cb.pack(fill='x')

        ttk.Label(form, text="Số điện thoại:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        so_dien_thoai_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)
        so_dien_thoai_entry.pack(fill='x')

        def save_reader():
            ma_doc = ma_doc_entry.get().strip()
            ho_ten = ho_ten_entry.get().strip()
            ngay_sinh = ngay_sinh_entry.get().strip()
            gioi_tinh = gioi_tinh_cb.get()
            dia_chi = dia_chi_entry.get().strip()
            chuc_vu = chuc_vu_cb.get().strip()
            so_dien_thoai = so_dien_thoai_entry.get().strip()

            if not all([ma_doc, ho_ten, gioi_tinh, dia_chi, chuc_vu, so_dien_thoai]):
                messagebox.showerror("Lỗi", "Các thông tin bắt buộc không được để trống.", parent=win)
                return

            try:
                reader_manager.add_reader(ma_doc, ho_ten, ngay_sinh, gioi_tinh, dia_chi, chuc_vu, so_dien_thoai)
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e), parent=win)
                return

            self.update_reader_list()
            logger.info(f"Thêm bạn đọc: {ma_doc}")
            messagebox.showinfo("Thông báo", f"Thêm bạn đọc {ho_ten} thành công!", parent=win)
            win.destroy()

        btn_f = ttk.Frame(form)
        btn_f.pack(pady=15, fill='x')
        ttk.Button(btn_f, text="Lưu",  command=save_reader,  bootstyle="success").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_f, text="Hủy",  command=win.destroy,  bootstyle="danger").pack(side=tk.LEFT, padx=5)

    # THAO TÁC CẬP NHẬT THÔNG TIN BẠN ĐỌC 
    def show_update_reader_window(self):
        logger.info("Mở cửa sổ cập nhật bạn đọc")
        if not self.reader_tree.selection():
            messagebox.showwarning("Thông báo", "Vui lòng chọn một bạn đọc cần cập nhật thông tin.")
            return

        selected      = self.reader_tree.selection()[0]
        reader_id_key = str(self.reader_tree.item(selected)['values'][0])

        reader = data_handler.readers_db[reader_id_key]
        win    = tk.Toplevel(self.root)
        win.title("Cập Nhật Thông Tin Bạn Đọc")
        win.geometry("500x520")
        win.grab_set()

        ttk.Label(win, text="Cập nhật thông tin bạn đọc",
                  font=("Arial Unicode MS", 14, "bold")).pack(pady=10)
        ttk.Label(win, text=f"Mã bạn đọc: {reader_id_key}  (không thể thay đổi)",
                  font=_FONT_BOLD, foreground="#c0392b").pack(pady=3)

        form = ScrolledFrame(win)
        form.pack(fill=BOTH, expand=YES, padx=20, pady=5)

        ttk.Label(form, text="Họ và tên:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        ho_ten_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)
        ho_ten_entry.insert(0, reader.ho_ten)
        ho_ten_entry.pack(fill='x')

        ttk.Label(form, text="Ngày sinh (DD/MM/YYYY):", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        ngay_sinh_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)
        ngay_sinh_entry.insert(0, reader.ngay_sinh)
        ngay_sinh_entry.pack(fill='x')

        ttk.Label(form, text="Giới tính:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        gioi_tinh_cb = ttk.Combobox(form, values=["Nam", "Nữ", "Khác"], state="readonly",
                                     width=48, font=_FONT_ENTRY)
        if reader.gioi_tinh in ["Nam", "Nữ", "Khác"]:
            gioi_tinh_cb.set(reader.gioi_tinh)
        else:
            gioi_tinh_cb.current(0)
        gioi_tinh_cb.pack(fill='x')

        ttk.Label(form, text="Địa chỉ:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        dia_chi_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)
        dia_chi_entry.insert(0, reader.dia_chi)
        dia_chi_entry.pack(fill='x')

        ttk.Label(form, text="Chức vụ:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        chuc_vu_cb = ttk.Combobox(form, values=["Giảng viên", "Sinh viên", "Khác"], state="readonly",
                                     width=48, font=_FONT_ENTRY)
        if reader.chuc_vu in ["Giảng viên", "Sinh viên", "Khác"]:
            chuc_vu_cb.set(reader.chuc_vu)
        else:
            chuc_vu_cb.current(0)
        chuc_vu_cb.pack(fill='x')

        ttk.Label(form, text="Số điện thoại:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        so_dien_thoai_entry = ttk.Entry(form, font=_FONT_ENTRY, width=50)
        so_dien_thoai_entry.insert(0, reader.so_dien_thoai)
        so_dien_thoai_entry.pack(fill='x')

        def update_reader():
            ho_ten        = ho_ten_entry.get().strip()
            ngay_sinh     = ngay_sinh_entry.get().strip()
            gioi_tinh     = gioi_tinh_cb.get()
            dia_chi       = dia_chi_entry.get().strip()
            chuc_vu       = chuc_vu_cb.get().strip()
            so_dien_thoai = so_dien_thoai_entry.get().strip()

            if not all([ho_ten, gioi_tinh, dia_chi, chuc_vu, so_dien_thoai]):
                messagebox.showerror("Lỗi", "Các thông tin bắt buộc không được để trống", parent=win)
                return

            try:
                reader_manager.update_reader(reader_id_key, ho_ten, ngay_sinh, gioi_tinh, dia_chi, chuc_vu, so_dien_thoai)
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e), parent=win)
                return

            self.update_reader_list()
            logger.info(f"Cập nhật bạn đọc: {reader_id_key}")
            messagebox.showinfo("Thông báo", f"Cập nhật thông tin bạn đọc {ho_ten} thành công!", parent=win)
            win.destroy()

        btn_f = ttk.Frame(form)
        btn_f.pack(fill='x', pady=15)
        ttk.Button(btn_f, text="Cập nhật thông tin", command=update_reader, bootstyle="success").pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_f, text="Hủy", command=win.destroy, bootstyle="secondary").pack(side=tk.RIGHT, padx=5)

    # THAO TÁC TÌM KIẾM THÔNG TIN BẠN ĐỌC 
    def show_search_reader_window(self):
        logger.info("Mở cửa sổ tìm kiếm bạn đọc")
        win = tk.Toplevel(self.root)
        win.title("Tìm Kiếm Thông Tin Bạn Đọc")
        win.geometry("900x480")
        win.grab_set()

        top = ttk.Frame(win)
        top.pack(fill='x', padx=15, pady=12)

        ttk.Label(top, text="Tìm theo:", font=_FONT_LABEL).pack(side=tk.LEFT)
        search_field_var = tk.StringVar(value="Họ tên")
        field_cb = ttk.Combobox(top, textvariable=search_field_var,
                                 values=["Mã bạn đọc", "Họ tên", "Số điện thoại", "Địa chỉ", "Chức vụ"],
                                 state="readonly", width=16, font=_FONT_ENTRY)
        field_cb.pack(side=tk.LEFT, padx=(4, 12))

        ttk.Label(top, text="Từ khóa:", font=_FONT_LABEL).pack(side=tk.LEFT)
        search_var = tk.StringVar()
        entry = ttk.Entry(top, font=_FONT_ENTRY, textvariable=search_var, width=30)
        entry.pack(side=tk.LEFT, padx=8)
        entry.focus()

        cols = ("Mã bạn đọc", "Họ và tên", "Ngày sinh", "Giới tính", "Địa chỉ", "Chức vụ","Số điện thoại")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110, anchor="center")
        tree.column("Họ và tên", width=190, anchor="w")
        tree.column("Địa chỉ",   width=190, anchor="center")
        tree.column("Chức vụ",   width=190, anchor="center")
        tree.pack(fill='both', expand=True, padx=15, pady=5)

        def do_search(event=None):
            kw    = search_var.get().strip()
            field = search_field_var.get()

            field_map = {
                "Mã bạn đọc":    "ma_ban_doc",
                "Họ tên":        "ho_ten",
                "Số điện thoại": "so_dien_thoai",
                "Địa chỉ":       "dia_chi",
                "Chức vụ":       "chuc_vu"
            }
            found = reader_manager.search_readers(kw, field_map.get(field, "ho_ten"))

            for item in tree.get_children():
                tree.delete(item)
            for r in found:
                tree.insert("", "end", values=(
                    r.ma_ban_doc, r.ho_ten, r.ngay_sinh, r.gioi_tinh, r.dia_chi,r.chuc_vu, r.so_dien_thoai))

            if found:
                messagebox.showinfo("Thông báo", f"Tìm thấy {len(found)} bạn đọc thỏa mãn yêu cầu.", parent=win)
            else:
                messagebox.showinfo("Thông báo", "Không tìm thấy bạn đọc thỏa mãn yêu cầu.", parent=win)

        entry.bind("<Return>", do_search)
        ttk.Button(top, text="Tìm kiếm", command=do_search, bootstyle="warning").pack(side=tk.LEFT, padx=8)

    # THAO TÁC XÓA BẠN ĐỌC 
    def delete_reader(self):
        if not self.reader_tree.selection():
            messagebox.showwarning("Thông báo", "Vui lòng chọn bạn đọc cần xóa.")
            return

        selected = self.reader_tree.selection()[0]
        reader_id_key = str(self.reader_tree.item(selected)['values'][0])
        reader = data_handler.readers_db.get(reader_id_key)
        if not reader:
            messagebox.showerror("Lỗi", f"Mã bạn đọc '{reader_id_key}' không tồn tại!")
            return

        dang_muon = [r for r in data_handler.tracking_records
                     if r.ma_ban_doc == reader_id_key and r.trang_thai in ("Đang mượn", "Quá hạn")]
        if dang_muon:
            qua_han = any(r.trang_thai == "Quá hạn" for r in dang_muon)
            messagebox.showerror("Thông báo",
                f"Không thể xóa bạn đọc này do bạn đọc đang mượn sách"
                f"{' (có sách mượn quá hạn)' if qua_han else ''}.")
            return

        ho_ten = reader.ho_ten if hasattr(reader, 'ho_ten') else reader.ten
        if not messagebox.askyesno("Xác nhận",
                f"Bạn có chắc chắc muốn xóa bạn đọc {ho_ten} hay không?"):
            return

        try:
            reader_manager.delete_reader(reader_id_key)
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
            return

        self.update_reader_list()
        messagebox.showinfo("Thông báo", "Đã xóa bạn đọc thành công!")

    # XÂY DỰNG TAB CHỨC NĂNG MƯỢN/TRẢ SÁCH
    def setup_tracking_tab(self):
        btn_frame = ttk.Frame(self.tracking_tab)
        btn_frame.pack(pady=15, padx=20, fill='x')

        for text, color, cmd in [
            ("Mượn sách","#1F8949", self.show_borrow_window),
            ("Trả sách","#166698", self.show_return_window),
            ("Kiểm tra lịch sử mượn sách","#C7673A", self.show_history_window),
            ("Kiểm tra sách quá hạn","#B52C28", self.show_overdue_books_window),
        ]:
            ctk.CTkButton(btn_frame, text=text, fg_color=color, corner_radius=5,
                          font=("Segoe UI", 13, "bold"), text_color="white",
                          command=cmd).pack(side=tk.LEFT, padx=5)

        body = ttk.Frame(self.tracking_tab)
        body.pack(fill='both', expand=True, padx=10, pady=5)

        tree_frame = ttk.Frame(body)
        tree_frame.pack(side=tk.LEFT, fill='both', expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tracking_tree = ttk.Treeview(
            tree_frame,
            columns=('Mã bạn đọc', 'Chức vụ','Mã sách', 'Tên sách', 'Ngày mượn', 'Ngày trả', 'Trạng thái'),
            yscrollcommand=tree_scroll.set,
            show="headings"
        )
        tree_scroll.config(command=self.tracking_tree.yview)

        col_w = {'Mã bạn đọc': 100,'Chức vụ':50, 'Mã sách': 90, 'Tên sách': 250,
                 'Ngày mượn': 120, 'Ngày trả': 120, 'Trạng thái': 110}
        for col, w in col_w.items():
            self.tracking_tree.heading(col, text=col)
            self.tracking_tree.column(col, width=w, anchor="center")
        self.tracking_tree.column('Chức vụ', anchor="center")
        self.tracking_tree.column('Tên sách', anchor="w")
        self.tracking_tree.pack(fill='both', expand=True)

        self.tracking_tree.tag_configure('oddrow',   background='#E8F4FA')
        self.tracking_tree.tag_configure('evenrow',  background='#FFFFFF')
        self.tracking_tree.tag_configure('overdue',  background='#fadbd8')

        # XÂY DỰNG KHUNG CHỨC NĂNG LỌC NHỮNG CUỐN SÁCH ĐƯỢC MƯỢN NHIỀU NHẤT
        side = ttk.Frame(body, relief="groove")
        side.pack(side=tk.RIGHT, fill='y', padx=(10, 0), pady=0)

        top_lf = ttk.LabelFrame(side, text="Top sách mượn nhiều nhất", padding=8)
        top_lf.pack(fill='x', padx=8, pady=8)

        ttk.Label(top_lf, text="Hiển thị Top:").pack(anchor="w")
        self.top_n_var = tk.StringVar(value="5")
        ttk.Combobox(top_lf, textvariable=self.top_n_var,
                     values=["3", "5", "10"],
                     state="readonly", width=10).pack(fill='x', pady=3)

        ctk.CTkButton(top_lf, text="Áp dụng", fg_color="#27ae60", text_color="white",
                      corner_radius=5, command=self._refresh_top_borrowed).pack(fill='x', pady=5)

        top_cols = ("Mã sách", "Tên sách", "Lượt mượn")
        self.top_tree = ttk.Treeview(side, columns=top_cols, show="headings", height=10)
        for c in top_cols:
            self.top_tree.heading(c, text=c)
            self.top_tree.column(c, width=140, anchor="center")
        self.top_tree.column("Tên sách", width=230, anchor="w")
        self.top_tree.pack(fill='both', expand=True, padx=8, pady=(0, 8))

        self._refresh_top_borrowed()

    # THAO TÁC KIỂM TRA VÀ CẬP NHẬT SÁCH QUÁ HẠN
    def check_and_update_overdue_books(self):
        tracking_manager.update_overdue_status()

    def _refresh_top_borrowed(self):
        for item in self.top_tree.get_children():
            self.top_tree.delete(item)
        try:
            top_n = int(self.top_n_var.get())
        except ValueError:
            top_n = 5
        records = tracking_manager.get_top_borrowed_books(top_n)
        for i, item in enumerate(records, start=1):
            tag = 'top1' if i == 1 else ('oddrow' if i % 2 == 0 else 'evenrow')
            self.top_tree.insert("", "end", values=(
                item["ma_sach"], item["ten_sach"], item["so_lan_muon"]
            ), tags=(tag,))

    def update_tracking_list(self):
        for item in self.tracking_tree.get_children():
            self.tracking_tree.delete(item)

        for i, r in enumerate(data_handler.tracking_records):
            if r.trang_thai == "Quá hạn":
                tag = 'overdue'
            elif i % 2 == 0:
                tag = 'oddrow'
            else:
                tag = 'evenrow'

            ngay_tra_display = r.ngay_tra if r.trang_thai == "Đã trả" else ""
            self.tracking_tree.insert("", "end", values=(
                r.ma_ban_doc, r.chuc_vu, r.ma_sach, r.ten_sach,
                r.ngay_muon, ngay_tra_display, r.trang_thai
            ), tags=(tag,))

        logger.debug("Đã cập nhật danh sách mượn/trả")
        self._refresh_top_borrowed()

    # THAO TÁC MƯỢN SÁCH 
    def show_borrow_window(self):
        logger.info("Mở cửa sổ mượn sách")
        win = tk.Toplevel(self.root)
        win.title("Mượn Sách")
        win.geometry("500x500")
        win.grab_set()

        ttk.Label(win, text="Mượn Sách", font=("Arial Unicode MS", 14, "bold")).pack(pady=10)

        form = ttk.Frame(win)
        form.pack(fill='x', padx=20)

        ttk.Label(form, text="Mã bạn đọc:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        reader_id_var = tk.StringVar()
        ttk.Entry(form, font=_FONT_ENTRY, textvariable=reader_id_var, width=50).pack(fill='x')

        ttk.Label(form, text="Mã sách:", font=_FONT_LABEL).pack(anchor="w", pady=(8, 0))
        book_id_var = tk.StringVar()
        ttk.Entry(form, font=_FONT_ENTRY, textvariable=book_id_var, width=50).pack(fill='x')

        info_label = ttk.Label(win, text="", font=("Arial Unicode MS", 10),
                                foreground="#34495e", wraplength=420, justify="left")
        info_label.pack(padx=20, pady=10, anchor="w")

        result_cache = {}

        confirm_btn = ctk.CTkButton(win, text="Xác nhận mượn sách",
                                     fg_color="#27ae60", text_color="white",
                                     corner_radius=5, state="disabled",
                                     command=lambda: confirm_borrow())
        confirm_btn.pack(fill='x', padx=20, pady=5)

        def check_info():
            reader_id = reader_id_var.get().strip()
            book_id   = book_id_var.get().strip()

            if not reader_id or not book_id:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Mã bạn đọc và Mã sách.", parent=win)
                return

            if reader_id not in data_handler.readers_db:
                messagebox.showerror("Lỗi", f"Mã bạn đọc {reader_id} không tồn tại trong hệ thống.", parent=win)
                return
            if book_id not in data_handler.books_db:
                messagebox.showerror("Lỗi", f"Mã sách {book_id} không tồn tại trong hệ thống.", parent=win)
                return

            reader = data_handler.readers_db[reader_id]
            book   = data_handler.books_db[book_id]

            result_cache['reader_id'] = reader_id
            result_cache['book_id']   = book_id
            ho_ten = reader.ho_ten if hasattr(reader, 'ho_ten') else reader.ten

            so_con_lai = tracking_manager.get_so_luong_con_lai(book_id)
            info_label.config(text=(
                f"Bạn đọc: {ho_ten}  (Mã: {reader_id})\n"
                f"Chức vụ: {reader.chuc_vu}\n"
                f"Sách:    {book.ten_sach}  (Mã: {book_id})\n"
                f"Số sách còn lại trong thư viện: {so_con_lai}\n"
                "Nhấn 'Xác nhận mượn sách' để hoàn tất."
            ))
            confirm_btn.configure(state="normal")

        def confirm_borrow():
            reader_id = result_cache.get('reader_id')
            book_id   = result_cache.get('book_id')
            if not reader_id:
                return

            reader = data_handler.readers_db.get(reader_id)
            chuc_vu = reader.chuc_vu if reader else ""

            try:
                tracking_manager.borrow_book(reader_id, book_id, chuc_vu)
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e), parent=win)
                confirm_btn.configure(state="disabled")
                return

            self.update_tracking_list()
            self.update_book_list()
            logger.info(f"Mượn sách {book_id} bởi {reader_id}")
            messagebox.showinfo("Thông báo", "Xác nhận mượn sách thành công!", parent=win)
            win.destroy()

        ctk.CTkButton(win, text="Kiểm tra thông tin", fg_color="#f39c12",
                      text_color="white", corner_radius=5,
                      command=check_info).pack(fill='x', padx=20, pady=(0, 5))

    # THAO TÁC TRẢ SÁCH 
    def show_return_window(self):
        logger.info("Mở cửa sổ trả sách")
        win = tk.Toplevel(self.root)
        win.title("Trả Sách")
        win.geometry("820x520")
        win.grab_set()

        ttk.Label(win, text="Trả Sách", font=("Arial Unicode MS", 14, "bold")).pack(pady=10)

        top = ttk.Frame(win)
        top.pack(fill='x', padx=15, pady=5)
        ttk.Label(top, text="Mã bạn đọc:", font=_FONT_LABEL).pack(side=tk.LEFT)
        reader_id_var = tk.StringVar()
        reader_id_entry = ttk.Entry(top, font=_FONT_ENTRY, textvariable=reader_id_var, width=20)
        reader_id_entry.pack(side=tk.LEFT, padx=8)
        reader_id_entry.focus()

        filter_frame = ttk.Frame(win)
        filter_frame.pack(fill='x', padx=15, pady=(0, 5))
        ttk.Label(filter_frame, text="Lọc:", font=_FONT_LABEL).pack(side=tk.LEFT)
        filter_combo = ttk.Combobox(filter_frame, values=["Tất cả", "Mã sách","Tên sách", "Trạng thái"],
                                    state="readonly", width=12)
        filter_combo.current(0)
        filter_combo.pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(filter_frame, font=_FONT_ENTRY, width=25)
        search_entry.pack(side=tk.LEFT, padx=5)

        cols = ("Mã sách", "Tên sách", "Ngày mượn", "Trạng thái")
        return_tree = ttk.Treeview(win, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            return_tree.heading(c, text=c)
            return_tree.column(c, width=130, anchor="center")
        return_tree.column("Tên sách", width=270, anchor="w")
        return_tree.pack(fill='both', expand=True, padx=15, pady=5)
        return_tree.tag_configure('overdue', background='#fadbd8')

        current_rows = []

        def load_books(event=None):
            reader_id = reader_id_var.get().strip()
            if not reader_id:
                return
            if reader_id not in data_handler.readers_db:
                messagebox.showerror("Lỗi", f"Mã bạn đọc {reader_id} không tồn tại trong hệ thống.", parent=win)
                return

            current_rows.clear()
            for r in data_handler.tracking_records:
                if r.ma_ban_doc == reader_id and r.trang_thai in ("Đang mượn", "Quá hạn"):
                    current_rows.append(r)
            apply_filter()

        def apply_filter(*args):
            mode    = filter_combo.get()
            keyword = search_entry.get().strip().lower()

            for item in return_tree.get_children():
                return_tree.delete(item)

            for r in current_rows:
                if mode == "Trạng thái" and keyword:
                    if keyword not in r.trang_thai.lower(): continue
                elif mode == "Mã sách" and keyword:
                    if keyword not in r.ma_sach.lower(): continue
                elif mode == "Tên sách" and keyword:
                    if keyword not in r.ten_sach.lower(): continue
                elif mode == "Tất cả" and keyword:
                    if keyword not in r.ma_sach.lower() and keyword not in r.trang_thai.lower() and keyword not in r.ten_sach.lower(): continue
                tag = 'overdue' if r.trang_thai == "Quá hạn" else ''
                return_tree.insert("", "end",
                    values=(r.ma_sach, r.ten_sach, r.ngay_muon, r.trang_thai),
                    tags=(tag,))

        reader_id_entry.bind("<Return>", load_books)
        search_entry.bind("<KeyRelease>", apply_filter)
        filter_combo.bind("<<ComboboxSelected>>", apply_filter)
        ttk.Button(top, text="Tìm", command=load_books, bootstyle="info").pack(side=tk.LEFT, padx=5)

        def return_book():
            sel = return_tree.selection()
            if not sel:
                messagebox.showwarning("Thông báo", "Vui lòng chọn một cuốn sách để trả.", parent=win)
                return

            values  = return_tree.item(sel[0], 'values')
            ma_sach = values[0]
            reader_id = reader_id_var.get().strip()

            try:
                tracking_manager.return_book(reader_id, ma_sach)
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e), parent=win)
                return

            self.update_tracking_list()
            self.update_book_list()
            logger.info(f"Trả sách {ma_sach} bởi {reader_id}")
            messagebox.showinfo("Thông báo", "Trả sách thành công!", parent=win)
            load_books()

        ctk.CTkButton(win, text="Trả sách", fg_color="#587F98", text_color="white",
                      corner_radius=5, command=return_book).pack(fill='x', padx=15, pady=10)

    # THAO TÁC KIỂM TRA LỊCH SỬ MƯỢN SÁCH
    def show_history_window(self):
        logger.info("Mở cửa sổ xem lịch sử mượn/trả")
        win = tk.Toplevel(self.root)
        win.title("Lịch Sử Mượn/Trả Sách")
        win.geometry("1900x800")

        search_frame = ttk.Frame(win)
        search_frame.pack(fill='x', padx=20, pady=15)
        ttk.Label(search_frame, text="Tìm theo Mã bạn đọc hoặc Mã sách:", font=_FONT_LABEL).pack(side=tk.LEFT)
        search_var = tk.StringVar()
        entry = ttk.Entry(search_frame, font=_FONT_ENTRY, textvariable=search_var, width=25)
        entry.pack(side=tk.LEFT, padx=8)
        entry.focus()

        cols = ('Mã bạn đọc', 'Tên bạn đọc', 'Chức vụ','Mã sách', 'Tên sách', 'Ngày mượn', 'Ngày trả', 'Trạng thái')
        tree = ttk.Treeview(win, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=130, anchor='center')
        tree.column('Tên bạn đọc', width=200, anchor='w')
        tree.column('Chức vụ', width=100, anchor='center')
        tree.column('Tên sách',    width=300, anchor='w')
        tree.pack(pady=5, padx=20, fill=BOTH, expand=True)
        tree.tag_configure('overdue', background='#fadbd8')

        def show_all():
            for item in tree.get_children():
                tree.delete(item)
            for i, h in enumerate(tracking_manager.get_borrow_history()):
                r = h["record"]
                ngay_tra_d = r.ngay_tra if r.trang_thai == "Đã trả" else ""
                tag = 'overdue' if r.trang_thai == "Quá hạn" else ('oddrow' if i % 2 == 0 else 'evenrow')
                tree.insert('', 'end', values=(
                    r.ma_ban_doc, h["ten_ban_doc"],r.chuc_vu, r.ma_sach, r.ten_sach,
                    r.ngay_muon, ngay_tra_d, r.trang_thai
                ), tags=(tag,))

        def search_history(event=None):
            keyword = search_var.get().strip()
            if not keyword:
                show_all()
                return

            bd_exist   = keyword in data_handler.readers_db
            sach_exist = keyword in data_handler.books_db
            if not bd_exist and not sach_exist:
                messagebox.showinfo("Thông báo",
                    f"Mã bạn đọc/Mã sách {keyword} không tồn tại trong hệ thống.", parent=win)
                return

            for item in tree.get_children():
                tree.delete(item)
            for i, h in enumerate(tracking_manager.get_borrow_history(keyword)):
                r = h["record"]
                ten_bd = h["ten_ban_doc"]
                ngay_tra_d = r.ngay_tra if r.trang_thai == "Đã trả" else ""
                tag = 'overdue' if r.trang_thai == "Quá hạn" else ('oddrow' if i % 2 == 0 else 'evenrow')
                tree.insert('', 'end', values=(
                    r.ma_ban_doc, ten_bd, r.chuc_vu, r.ma_sach, r.ten_sach,
                    r.ngay_muon, ngay_tra_d, r.trang_thai
                ), tags=(tag,))

        entry.bind("<Return>", search_history)
        ttk.Button(search_frame, text="Tìm kiếm", command=search_history, bootstyle="warning").pack(side=tk.LEFT, padx=5)
        show_all()

    # THAO TÁC KIỂM TRA SÁCH QUÁ HẠN 
    def show_overdue_books_window(self):
        logger.info("Mở cửa sổ danh sách sách quá hạn")

        self.check_and_update_overdue_books()
        self.update_tracking_list()

        win = tk.Toplevel(self.root)
        win.title("Danh Sách Sách Quá Hạn")
        win.geometry("1600x800")

        search_frame = ttk.Frame(win)
        search_frame.pack(fill='x', padx=20, pady=15)
        ttk.Label(search_frame, text="Lọc theo Mã bạn đọc:", font=_FONT_LABEL).pack(side=tk.LEFT)
        ma_bd_var = tk.StringVar()
        entry = ttk.Entry(search_frame, font=_FONT_ENTRY, textvariable=ma_bd_var, width=20)
        entry.pack(side=tk.LEFT, padx=8)

        cols = ("Mã bạn đọc","Tên bạn đọc","Chức vụ", "Mã sách", "Tên sách", "Ngày mượn", "Số ngày quá hạn", "Tiền phạt")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=130, anchor="center")
        tree.column("Tên bạn đọc", width=200, anchor="w")
        tree.column("Tên sách",    width=300, anchor="w")
        tree.column("Chức vụ",    width=300, anchor="center")
        tree.column("Tiền phạt",   width=150, anchor="center")
        tree.pack(fill='both', expand=True, padx=20, pady=5)
        tree.tag_configure('overdue', background='#fadbd8')

        fine_frame = ttk.Frame(win)
        fine_frame.pack(fill='x', padx=20, pady=(0, 5))
        fine_label = ttk.Label(fine_frame, text="", font=("Arial Unicode MS", 11, "bold"),
                                foreground="#c0392b")
        fine_label.pack(side=tk.LEFT)

        def load_overdue(event=None):
            ma_bd_filter = ma_bd_var.get().strip()

            for item in tree.get_children():
                tree.delete(item)
            fine_label.config(text="")

            try:
                records = tracking_manager.get_overdue_records(ma_bd_filter or None)
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e), parent=win)
                return
            
            tong_tien_phat = 0
            tong_sach = 0
            tong_ngay = 0

            for item in records:
                r = item["record"]
                so_ngay = item["so_ngay_qua_han"]
                muc_phat = item["muc_phat"]
                chuc_vu = item["chuc_vu"]
                tien_phat = item["tien_phat"]

                tong_tien_phat += tien_phat
                tong_sach += 1
                tong_ngay += so_ngay

                tien_phat_str = f"{tien_phat:,.0f} đ" if tien_phat > 0 else "0 đ"
                tree.insert("", "end", values=(
                    r.ma_ban_doc, item["ten_ban_doc"], r.chuc_vu, r.ma_sach, r.ten_sach,
                    r.ngay_muon, f"{so_ngay} ngày", tien_phat_str
                ), tags=('overdue',))

            if ma_bd_filter and tong_sach > 0:
                ten_bd = records[0]["ten_ban_doc"]
                fine_label.config(
                    text=f"Bạn đọc {ten_bd} ({ma_bd_filter})  —  "
                         f"{tong_sach} sách quá hạn  —  "
                         f"Tổng tiền phạt: {tong_tien_phat:,.0f} đ  "
                )
                messagebox.showinfo(
                    "Thông báo tiền phạt",
                    f"Bạn đọc: {ten_bd} (Mã: {ma_bd_filter})\n"
                    f"Chức vụ: {chuc_vu}\n"
                    f"Mức phạt: {muc_phat} đồng/tuần\n"
                    f"Tổng số sách quá hạn: {tong_sach} cuốn\n"
                    f"Tổng số ngày quá hạn: {tong_ngay} ngày\n"
                    f"Tổng tiền phạt cần nộp: {tong_tien_phat:,.0f} đồng",
                    parent=win
                )

        entry.bind("<Return>", load_overdue)
        ttk.Button(search_frame, text="Lọc", command=load_overdue, bootstyle="danger").pack(side=tk.LEFT, padx=5)
        ttk.Button(win, text="Đóng", command=win.destroy, bootstyle="secondary").pack(pady=10)

        load_overdue()
