
from fastapi import FastAPI, Request
from scripts import *
import aiomysql
import asyncio
from typing import List, Dict
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, FileResponse


from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")
from fastapi.staticfiles import StaticFiles

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
cert_template = env.get_template('certificate/index.html')

import weasyprint

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# CREATE_TABLE_QUERY = """
# CREATE TABLE IF NOT EXISTS certificates (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     certificate_id VARCHAR(255),
#     name VARCHAR(255),
#     issuer VARCHAR(255),
#     issue_date INT
# )
# """
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



# async def create_cert_table():
    
#     try:
#         async with aiomysql.connect(**DB_CONFIG) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute(CREATE_TABLE_QUERY)
#                 await conn.commit()
#                 print("Table 'certificates' created successfully.")
#     except Exception as e:
#         print(f"Error creating table: {e}")
            
            
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
        # await create_cert_table()
        
        # Store certificate data
        # await store_certificate_data(certificate_response)
        
        # Return the CertificateResponse as the response
        return certificate_response
    
    return {"error": "Failed to issue certificate"}

@app.post("/verify-certificate")
async def verify_certificate_endpoint(certificate_id: str):
    if not certificate_id:
        return {"error": "Missing certificate ID"}
    else:
        # Verify the certificate
        result = verify_certificate(certificate_id)
        if result:
            return {"message": "Certificate is valid"}
        else:
            return {"message": "Certificate not found or invalid"}

# async def store_certificate_data(certificate_data: CertificateResponse):
#     try:
#         async with aiomysql.connect(**DB_CONFIG) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute(
#                     "INSERT INTO certificates (certificate_id, name, issuer, issue_date) VALUES (%s, %s, %s, %s)",
#                     (certificate_data.certificate_id, certificate_data.name, certificate_data.issuer, certificate_data.issue_date)
#                 )
#                 await conn.commit()
#                 print("Certificate data stored successfully.")
#     except Exception as e:
#         print(f"Error storing certificate data: {e}")

@app.get("/certificates")
async def generate_certificates(request: Request, data: CertificateResponse):
    # Fetch all certificate data
    name = data.name
    issuer = data.issuer
    cert_id = data.certificate_id
    issuer_date = data.issue_date

    # Generate the certificate HTML
    certificate_html = templates.TemplateResponse(
        "certificate/index.html",
        {"request": request, "name": name, "issuer": issuer, "cert_id": cert_id, "issuer_date": issuer_date},
    ).body.decode()

    # Convert the HTML to a PDF
    pdf_file_path = convert_to_pdf(certificate_html)

    if pdf_file_path:
        # Return the PDF as a response
        return FileResponse(pdf_file_path, headers={"Content-Disposition": "inline; filename=certificate.pdf"}, media_type="application/pdf")
    else:
        return "Failed to generate the certificate PDF"
    
    

def convert_to_pdf(certificate_html):
    # Generate a PDF from the certificate HTML
    pdf_file_path = "certs/certificate.pdf"

    # Use WeasyPrint to convert HTML to PDF
    try:
        html = weasyprint.HTML(string=certificate_html)
        pdf = html.write_pdf()

        # Save the PDF to a file
        with open(pdf_file_path, "wb") as pdf_file:
            pdf_file.write(pdf)

        return pdf_file_path  # Return the path to the saved PDF
    except Exception as e:
        # Handle any exceptions that may occur during PDF conversion
        print(f"Error converting HTML to PDF: {e}")
        return None
