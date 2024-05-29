import json
import mysql.connector

# 連接到MySQL伺服器（不連接到具體資料庫）
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12345678'
)
cursor = conn.cursor()

# 創建資料庫
cursor.execute("CREATE DATABASE IF NOT EXISTS attractions")

# 連接到新創建的資料庫
conn.database = 'attractions'



# 創建表格
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS mrt_stations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attractions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    address VARCHAR(255),
    rate INT,
    date DATE,
    longitude DECIMAL(10, 6),
    latitude DECIMAL(10, 6),
    category_id INT,
    memo_time TEXT,
    poi CHAR(1),
    file JSON,
    avBegin DATE,
    avEnd DATE,
    mrt_id INT,
    ref_wp VARCHAR(255),
    langinfo VARCHAR(255),
    serial_no VARCHAR(255),
    idpt VARCHAR(255),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (mrt_id) REFERENCES mrt_stations(id),
    direction TEXT
)
""")

# 讀取JSON文件
with open('data/taipei-attractions.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 插入類別數據並創建映射字典
categories = set(entry['CAT'] for entry in data['result']['results'])
category_map = {}
for category in categories:
    cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category,))
    category_map[category] = cursor.lastrowid



# 插入捷運站數據並創建映射字典
mrt_stations = set(entry['MRT'] for entry in data['result']['results'] if entry['MRT'])
mrt_map = {}
for mrt in mrt_stations:
    cursor.execute("INSERT INTO mrt_stations (name) VALUES (%s)", (mrt,))
    mrt_map[mrt] = cursor.lastrowid





# 插入景點數據
for entry in data['result']['results']:
    files = entry.get('file', '')
    file_urls = files.split('https://')
    file_urls = ['https://' + url for url in file_urls if url.lower().endswith(('.jpg', '.png'))]
    filtered_files = json.dumps(file_urls)  # 將過濾後的URL轉換為JSON數組
    mrt_id = mrt_map.get(entry['MRT'], None)
    category_id = category_map.get(entry['CAT'], None)

    sql = """
    INSERT INTO attractions (
        name, description, address, rate, date, longitude, latitude, category_id, memo_time, poi, file, avBegin, avEnd, mrt_id, ref_wp, langinfo, serial_no, idpt, direction
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
    """
    values = (
        entry['name'], entry['description'], entry['address'], entry['rate'], entry['date'],
        float(entry['longitude']), float(entry['latitude']), category_id, entry['MEMO_TIME'], entry['POI'],
        filtered_files, entry['avBegin'], entry['avEnd'], mrt_id, entry['REF_WP'], entry['langinfo'],
        entry['SERIAL_NO'], entry['idpt'], entry['direction']
    )
    cursor.execute(sql, values)

# 提交景點變更
conn.commit()

# 檢查插入結果


# 關閉連接
cursor.close()
conn.close()