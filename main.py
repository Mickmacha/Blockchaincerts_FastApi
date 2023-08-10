
from fastapi import FastAPI
from scripts import *
import aiomysql
import asyncio
from typing import List, Dict

app = FastAPI()

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "lms123",
    "db": "django_lms",
}

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    certificate_id INT,
    name VARCHAR(255),
    issuer VARCHAR(255),
    issue_date INT
)
"""

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
   
    # Process the fetched data
    processed_data = []
    for user in data:
        processed_user = {
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": f"{user['first_name']} {user['last_name']}",
            # ... add more processed fields if needed
        }
        processed_data.append(processed_user)

    return processed_data
#command to list all mysql tables in a database
#show tables from django_lms;



async def create_cert_table():
    
    try:
        async with aiomysql.connect(**DB_CONFIG) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(CREATE_TABLE_QUERY)
                await conn.commit()
                print("Table 'certificates' created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")
            
            
@app.post("/issue-certificate")
async def issue_certificate_endpoint(data: Dict):
    name = data.get("name")
    issuer = data.get("issuer")
    issue_date = data.get("issue_date")
    if not all([name, issuer, issue_date]):
        return {"error": "Missing required data fields"}
    
    certificate = issue_certificate(name, issuer, issue_date)
    
    # Create 'certificates' table if it doesn't exist
    await create_cert_table()
    #cant currently store cert data because ill need to use get cer function for that and ill need to know index
    
    # await store_certificate_data(certificate)
    return certificate
            
async def store_certificate_data(certificate_data):
    

    try:
        async with aiomysql.connect(**DB_CONFIG) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO certificates (certificate_id, name, issuer, issue_date) VALUES (%s, %s, %s, %s)",
                    (certificate_data["certificate_id"], certificate_data["name"], certificate_data["issuer"], certificate_data["issue_date"])
                )
                await conn.commit()
                print("Certificate data stored successfully.")
    except Exception as e:
        print(f"Error storing certificate data: {e}")
