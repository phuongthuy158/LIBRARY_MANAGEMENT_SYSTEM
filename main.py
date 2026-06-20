import gui
import data_handler
import ttkbootstrap as ttk
from tkinter import messagebox

if __name__ == "__main__":
    from logger import logger
    logger.info("Khởi động ứng dụng")
    try:
        data_handler.load_data()
        logger.info("Đã tải dữ liệu thành công")
        root = ttk.Window(themename="cosmo")
        app = gui.LibraryManagementSystem(root)
        root.mainloop()
        logger.info("Đã lưu dữ liệu và kết thúc ứng dụng")
    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {str(e)}", exc_info=True)
        messagebox.showerror("Lỗi", "Có lỗi xảy ra khi chạy ứng dụng!")