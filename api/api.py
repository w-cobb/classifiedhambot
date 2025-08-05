from fastapi import FastAPI
from dotenv import load_dotenv
import psycopg
import os

load_dotenv()
user = os.getenv("USER")
password = os.getenv("PASSWORD")
dbname = os.getenv("DBNAME")

conn_string = f"dbname={dbname} user={user} password={password} host=localhost"

with psycopg.connect(conn_string) as conn:
    print("Connected")
    with conn.cursor() as cur:
        cur.execute("select * from \"bot schema\".trackers")
        print(cur.fetchall())

app = FastAPI()

@app.get("/")
async def root():
    return {'message': 'Hello World'}

@app.get('/trackers')
async def get_trackers():
    return {'trackers': ['test1', 'test2', 'test3']}

@app.get('/listings')
async def get_listings():
    return {'listings': ['listing1','listing2','listing3']}

@app.get('/alerts')
async def get_alerts():
    return {'alerts': ['alert1','alert2','alert3']}