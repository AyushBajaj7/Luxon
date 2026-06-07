import os
from dotenv import load_dotenv
import psycopg

load_dotenv('d:/projects/Luxon/.env')
conn = psycopg.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute("SELECT image_url FROM products WHERE name LIKE '%Caviar%'")
print(cur.fetchone()[0])
