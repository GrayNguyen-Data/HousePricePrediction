# Mục tiêu
# Kết nối đến cơ sở dữ liệu PostgreSQL và trả về đối tượng kết nối và con trỏ để thực hiện các câu query


import psycopg2

def connect():
    try:
        conn = psycopg2.connect(
            host = "localhost",
            database = "house_price",
            user = "postgres",
            password = "1",
            port = 5432)
        cur = conn.cursor() # Con trỏ để thực hiện các câu query
        print("Database connected successfully!")
        return conn, cur
    except Exception as e:
        print(f"Error connecting to database: {e}")
