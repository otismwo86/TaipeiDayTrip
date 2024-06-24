import json
import mysql.connector


conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password="12345678",
    database="attractions"
)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE Bookings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    attraction_id INT NOT NULL,
                    date DATE NOT NULL,
                    time VARCHAR(20) NOT NULL,
                    price INT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES member(id),
                    FOREIGN KEY (attraction_id) REFERENCES attractions(id)
);""")
conn.commit()

cursor.close()
conn.close()

