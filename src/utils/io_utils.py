
import pandas as pd
import os
import shutil
from datetime import datetime

class IOUtils:
    @staticmethod
    def load_csv(path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Không tìm thấy file tại: {path}")
        return pd.read_csv(path, encoding='utf-8-sig')

    @staticmethod
    def save_csv(df, path, backup=True):
        if backup and os.path.exists(path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{path}.{timestamp}.bak"
            shutil.copy2(path, backup_path)
            print(f"✅ Đã tạo bản sao lưu tại: {backup_path}")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False, encoding='utf-8-sig')
        print(f"💾 Đã lưu dữ liệu vào: {path}")

    @staticmethod
    def ensure_dir(path):
        if not os.path.exists(path):
            os.makedirs(path)
