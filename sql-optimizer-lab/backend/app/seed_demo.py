from pathlib import Path
import random, sqlite3

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "demo.db"
DB.parent.mkdir(parents=True, exist_ok=True)
if DB.exists(): DB.unlink()
con = sqlite3.connect(DB)
cur = con.cursor()
cur.executescript('''
CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL, status TEXT NOT NULL);
CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, created_at TEXT NOT NULL, total_cents INTEGER NOT NULL,
  FOREIGN KEY(customer_id) REFERENCES customers(id));
CREATE TABLE order_items(id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL, sku TEXT NOT NULL, qty INTEGER NOT NULL,
  FOREIGN KEY(order_id) REFERENCES orders(id));
CREATE INDEX idx_orders_customer_created ON orders(customer_id, created_at);
CREATE INDEX idx_customers_status ON customers(status);
CREATE INDEX idx_items_order ON order_items(order_id);
''')
for i in range(1, 501):
    cur.execute("INSERT INTO customers VALUES (?,?,?)", (i, f"Customer {i}", "active" if i % 5 else "inactive"))
for i in range(1, 10001):
    cid = random.randint(1,500)
    day = random.randint(1, 365)
    created = f"2026-{'%02d'%((day-1)//30+1)}-{'%02d'%((day-1)%28+1)} 12:00:00"
    cur.execute("INSERT INTO orders VALUES (?,?,?,?)", (i,cid,created,random.randint(500,50000)))
    for j in range(random.randint(1,3)):
        cur.execute("INSERT INTO order_items VALUES (?,?,?,?)", (i*3+j, i, f"SKU-{random.randint(1,100)}", random.randint(1,5)))
con.commit(); con.close()
print(DB)
