from fastapi import Depends, FastAPI
from dotenv import load_dotenv
import psycopg
import os

load_dotenv()
user = os.getenv("USER")
password = os.getenv("PASSWORD")
dbname = os.getenv("DBNAME")
hostname = os.getenv("HOSTNAME")

conn_string = f"dbname={dbname} user={user} password={password} host={hostname}"

with psycopg.connect(conn_string) as conn:
    print("Connected")
    with conn.cursor() as cur:
        cur.execute("show search_path")
        print(cur.fetchall())

app = FastAPI()

async def get_db_conn():
    async with await psycopg.AsyncConnection.connect(conn_string) as conn:
        yield conn

@app.get("/")
async def root():
    return {'message': 'Hello World'}

@app.get('/trackers')
async def get_trackers(conn = Depends(get_db_conn)):
    response = []
    async with conn.cursor() as cur:
        await cur.execute("select * from trackers")
        response = await cur.fetchall()
    return response

@app.get('/listings')
async def get_listings(conn = Depends(get_db_conn)):
    response = []
    async with conn.cursor() as cur:
        await cur.execute("select * from listings")
        response = await cur.fetchall()
    return response

@app.get('/alerts')
async def get_alerts(conn = Depends(get_db_conn)):
    response = []
    async with conn.cursor() as cur:
        await cur.execute("select * from alerts")
        response = await cur.fetchall()
    return response