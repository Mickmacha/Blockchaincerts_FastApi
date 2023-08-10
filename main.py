
from fastapi import FastAPI
from scripts import *
import aiomysql
import asyncio

app = FastAPI()

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "lms123",
    "db": "django_lms",
}
async def fetch_data_from_mysql(query):
    async with aiomysql.connect(**DB_CONFIG) as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            result = await cursor.fetchall()
    return result

@app.get("/fetch-data")
async def fetch_data():
    query = "SELECT * FROM django_lms.users_user"
    data = await fetch_data_from_mysql(query)
    return data
#command to list all mysql tables in a database
#show tables from django_lms;
