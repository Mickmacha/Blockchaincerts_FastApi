
from fastapi import FastAPI
from scripts import *
import aiomysql
import asyncio
from typing import List, Dict
from pydantic import BaseModel
app = FastAPI()
import base64


CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    certificate_id VARCHAR(255),
    name VARCHAR(255),
    issuer VARCHAR(255),
    issue_date INT
)
"""
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "lms123",
    "db": "django_lms",
}
 
class CertificateCreateRequest(BaseModel):
    name: str
    issuer: str
    issue_date: int

class CertificateResponse(BaseModel):
    certificate_id: str
    name: str
    issuer: str
    issue_date: int

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
            
            
@app.post("/issue-certificate", response_model=CertificateResponse)
async def issue_certificate_endpoint(data: CertificateCreateRequest):
    name = data.name
    issuer = data.issuer
    issue_date = data.issue_date
    
    if not all([name, issuer, issue_date]):
        return {"error": "Missing required data fields"}
    
    # Issue the certificate and get the certificate data
    certificate_data = issue_certificate(name, issuer, issue_date)
    print(certificate_data)
    if certificate_data:
        # Create a CertificateResponse object with the certificate data
        certificate_response = CertificateResponse(
            certificate_id=certificate_data["id"],
            name=certificate_data["name"],
            issuer=certificate_data["issuer"],
            issue_date=certificate_data["issueDate"],
        )
        
        # Create 'certificates' table if it doesn't exist
        await create_cert_table()
        
        # Store certificate data
        await store_certificate_data(certificate_response)
        
        # Return the CertificateResponse as the response
        return certificate_response
    
    return {"error": "Failed to issue certificate"}

async def store_certificate_data(certificate_data: CertificateResponse):
    try:
        async with aiomysql.connect(**DB_CONFIG) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO certificates (certificate_id, name, issuer, issue_date) VALUES (%s, %s, %s, %s)",
                    (certificate_data.certificate_id, certificate_data.name, certificate_data.issuer, certificate_data.issue_date)
                )
                await conn.commit()
                print("Certificate data stored successfully.")
    except Exception as e:
        print(f"Error storing certificate data: {e}")
