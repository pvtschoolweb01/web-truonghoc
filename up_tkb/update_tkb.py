import mysql.connector
import pandas as pd
import os
import re

# ====== Cấu hình MySQL ======
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "thoikhoabieu_db"
}

TABLE_NAME = "app_thoikhoabieu"

FILES = [
    (r"D:\School_website\schoolweb\up_tkb\1.xlsx", "Sáng"),
    (r"D:\School_website\schoolweb\up_tkb\2.xlsx", "Chiều")
]

def clean_subject(text):
    """
    - Chuyển các dash lạ thành "-"
    - Chuẩn hóa khoảng trắng
    - Tách môn và GV, đưa GV vào ngoặc, giữ nguyên phần ngoặc gốc
    """
    if not isinstance(text, str):
        return ""

    # Replace các ký tự dash lạ bằng "-"
    for dash in ["–", "—", "−", "‒", "―", "─", ":", "：", "‐", "⁃", "﹣", "－"]:
        text = text.replace(dash, "-")

    # Chuẩn hóa khoảng trắng
    text = re.sub(r'\s+', ' ', text).replace('\xa0', ' ').strip()
    text = re.sub(r'\s*-\s*', '-', text)  # xóa khoảng trắng quanh dash

    # Nếu có dash, tách môn và GV, đưa GV vào ngoặc
    if '-' in text:
        parts = text.split('-', 1)
        mon = parts[0].strip()
        gv = parts[1].strip()  # giữ nguyên (A) nếu có
        text = f"{mon}\n({gv})"

    return text


def extract_lop(header):
    """Lấy tên lớp từ header cột"""
    if not isinstance(header, str):
        return ""
    
    header = header.split("(")[0].strip()
    header = header.replace(" ", "")
    
    m = re.search(r"\d{2}[A-Za-z]\d*", header)
    if m:
        return m.group(0)
    
    tokens = header.split()
    for t in tokens:
        if re.search(r"\d", t) and re.search(r"[A-Za-zÀ-ỹ]", t):
            return t
    return tokens[0] if tokens else ""

def to_int_safe(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    if s == "":
        return None
    try:
        f = float(s)
        return int(f)
    except:
        m = re.search(r"\d+", s)
        if m:
            return int(m.group(0))
    return None

def read_excel(file_path, buoi):
    print(f"📄 Đang đọc file: {file_path} ({buoi})...")
    try:
        xls = pd.ExcelFile(file_path)
    except Exception as e:
        print(f"❌ Không đọc được file {file_path}: {e}")
        return pd.DataFrame(columns=["lop", "thu", "buoi", "tiet", "mon"])

    all_rows = []

    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        df = df.dropna(how="all")
        if df.shape[1] < 3:
            continue
        df.columns = [str(c).strip() for c in df.columns]

        col_names = df.columns.tolist()
        lop_headers = [extract_lop(c) for c in col_names[2:]]

        last_thu = None
        for idx, row in df.iterrows():
            thu_raw = row.iloc[0]
            tiet_raw = row.iloc[1]

            thu = to_int_safe(thu_raw) if pd.notna(thu_raw) else last_thu
            tiet = to_int_safe(tiet_raw)

            if thu is None or tiet is None:
                continue
            last_thu = thu

            for col_idx, col in enumerate(col_names[2:], start=2):
                mon_raw = row.iloc[col_idx]
                if pd.isna(mon_raw) or str(mon_raw).strip() == "":
                    continue
                mon = clean_subject(str(mon_raw))
                lop = lop_headers[col_idx - 2]
                if not lop or mon.strip() == "":
                    continue
                all_rows.append((lop, int(thu), str(buoi), int(tiet), mon))

    return pd.DataFrame(all_rows, columns=["lop", "thu", "buoi", "tiet", "mon"])

def update_mysql(df):
    if df.empty:
        print("⚠️ Không có dữ liệu hợp lệ để chèn.")
        return

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Xóa dữ liệu cũ
    cursor.execute(f"DELETE FROM {TABLE_NAME}")
    print("🧹 Đã xóa dữ liệu cũ trong bảng.")

    sql = f"INSERT INTO {TABLE_NAME} (lop, thu, buoi, tiet, mon) VALUES (%s, %s, %s, %s, %s)"
    data = df.values.tolist()

    batch_size = 1000
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        cursor.executemany(sql, batch)
        conn.commit()

    print(f"✅ Đã nhập {len(data)} dòng dữ liệu mới.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("📂 Thư mục hiện tại:", os.getcwd())
    print("📄 Files trong thư mục:", os.listdir())

    all_data = pd.DataFrame(columns=["lop", "thu", "buoi", "tiet", "mon"])
    for file_name, buoi in FILES:
        if os.path.exists(file_name):
            df = read_excel(file_name, buoi)
            all_data = pd.concat([all_data, df], ignore_index=True)
        else:
            print(f"⚠️ Không tìm thấy file: {file_name}")

    print(f"Tổng số dòng đọc được: {len(all_data)}")
    update_mysql(all_data)
