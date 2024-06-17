import json
import mysql.connector


conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password="12345678",
    database="attractions"
)
cursor = conn.cursor()

cursor.execute("""Create table member(
               id INT Primary KEY AUTO_INCREMENT, 
               name VARCHAR(255) NOT NULL,
               email VARCHAR(255) NOT NULL UNIQUE,
               password VARCHAR(255) NOT NULL,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
               )""")
conn.commit()

cursor.close()
conn.close()

