from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect('kiston_cafe.db')
    c = conn.cursor()
    # ตรวจสอบว่ามีคอลัมน์ customer_name หรือยัง ถ้าไม่มีให้เพิ่ม
    try:
        c.execute("ALTER TABLE sales ADD COLUMN customer_name TEXT")
    except:
        pass # ถ้ามีอยู่แล้วก็ข้ามไป
    
    c.execute('''CREATE TABLE IF NOT EXISTS sales
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  customer_name TEXT, 
                  price INTEGER, 
                  points INTEGER, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.get("/calculate/{name}/{price}")
def calculate_points_api(name: str, price: int):
    points = price // 50
    if price >= 500:
        points = points + 5
        
    conn = sqlite3.connect('kiston_cafe.db')
    c = conn.cursor()
    c.execute("INSERT INTO sales (customer_name, price, points) VALUES (?, ?, ?)", (name, price, points))
    conn.commit()
    conn.close()
    
    return {"status": "success", "name": name, "points": points, "message": "จดลงสมุดเรียบร้อย!"}

@app.get("/summary")
def get_summary():
    conn = sqlite3.connect('kiston_cafe.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(price), SUM(points) FROM sales")
    result = c.fetchone()
    conn.close()
    return {
        "total_customers": result[0] or 0,
        "total_revenue": result[1] or 0,
        "total_points_given": result[2] or 0
    }
@app.get("/history/{name}")
def get_customer_history(name: str):
    conn = sqlite3.connect('kiston_cafe.db')
    c = conn.cursor()
    # สั่งให้ SQL ไปหาข้อมูลเฉพาะชื่อนั้นๆ แล้วรวมแต้มให้ด้วย
    c.execute("SELECT customer_name, SUM(price), SUM(points), COUNT(*) FROM sales WHERE customer_name = ?", (name,))
    result = c.fetchone()
    conn.close()
    
    return {
        "name": result[0] or name,
        "total_spent": result[1] or 0,
        "total_points": result[2] or 0,
        "visit_count": result[3] or 0
    }