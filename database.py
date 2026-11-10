
import sqlite3
from pathlib import Path
from datetime import datetime
import os

DB_PATH = Path(os.getenv("DB_PATH", "soap_store.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            discount INTEGER DEFAULT 0,
            description TEXT DEFAULT '',
            image TEXT DEFAULT '',
            stock INTEGER DEFAULT 50,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            address TEXT NOT NULL,
            items_json TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'Received',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            rating INTEGER,
            message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            seed = [
                ("Rose Glow Soap","Floral",149,15,"A gentle, fragrant bathing bar with a soft floral feel.","rose.svg",50),
                ("Aloe Vera Fresh","Herbal",129,10,"A refreshing everyday bar inspired by aloe vera.","aloe.svg",50),
                ("Neem Purity Soap","Herbal",119,0,"A clean, crisp bathing bar for a fresh start.","neem.svg",50),
                ("Activated Charcoal","Premium",179,12,"A deep-toned premium bar with a bold, modern feel.","charcoal.svg",40),
                ("Herbal Garden Soap","Herbal",139,10,"A botanical blend for a calm bathing ritual.","herbal.svg",50),
                ("Sandalwood Luxe","Premium",199,15,"Warm sandalwood-inspired fragrance in a luxe bar.","sandalwood.svg",35),
                ("Handcrafted Artisan","Handmade",229,0,"Small-batch inspired artisan soap with a handcrafted look.","handmade.svg",25),
                ("Classic Bath Bar","Daily Care",99,5,"A simple, creamy-feel bath bar for everyday use.","classic.svg",60),
            ]
            conn.executemany("""INSERT INTO products
                (name,category,price,discount,description,image,stock)
                VALUES (?,?,?,?,?,?,?)""", seed)

def list_products(search="", category="All", include_inactive=False):
    sql = "SELECT * FROM products WHERE 1=1"
    args = []
    if not include_inactive:
        sql += " AND active=1"
    if search:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        args += [f"%{search}%", f"%{search}%"]
    if category and category != "All":
        sql += " AND category=?"
        args.append(category)
    sql += " ORDER BY id DESC"
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]

def get_product(product_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
        return dict(row) if row else None

def save_product(data, product_id=None):
    fields = ("name","category","price","discount","description","image","stock","active")
    values = [data.get(k) for k in fields]
    with get_connection() as conn:
        if product_id:
            conn.execute("""UPDATE products SET name=?,category=?,price=?,discount=?,
                description=?,image=?,stock=?,active=? WHERE id=?""", values+[product_id])
        else:
            conn.execute("""INSERT INTO products
                (name,category,price,discount,description,image,stock,active)
                VALUES (?,?,?,?,?,?,?,?)""", values)

def delete_product(product_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM products WHERE id=?", (product_id,))

def create_order(customer_name, mobile, address, items, total):
    import json
    with get_connection() as conn:
        cur = conn.execute("""INSERT INTO orders
            (customer_name,mobile,address,items_json,total)
            VALUES (?,?,?,?,?)""",
            (customer_name,mobile,address,json.dumps(items, ensure_ascii=False),total))
        return cur.lastrowid

def get_orders():
    import json
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["items"] = json.loads(d.pop("items_json"))
            result.append(d)
        return result

def update_order_status(order_id, status):
    with get_connection() as conn:
        conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))

def add_feedback(name, rating, message):
    with get_connection() as conn:
        conn.execute("INSERT INTO feedback(customer_name,rating,message) VALUES (?,?,?)",
                     (name,rating,message))

def get_feedback():
    with get_connection() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM feedback ORDER BY id DESC").fetchall()]
