import logging
from datetime import datetime
import os

def setup_logger():
    # Tạo thư mục logs nếu chưa tồn tại
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Tạo tên file log với timestamp
    log_filename = f'logs/library_system_{datetime.now().strftime("%Y%m%d")}.log'
    
    # Cấu hình logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # In ra console
        ]
    )
    
    return logging.getLogger(__name__)

# Khởi tạo logger
logger = setup_logger()