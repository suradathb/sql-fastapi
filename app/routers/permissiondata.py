from fastapi import APIRouter,HTTPException,UploadFile, File
from pydantic import BaseModel
import asyncio
from pyppeteer import launch
from fastapi.responses import JSONResponse
from openpyxl import load_workbook


router = APIRouter(
    prefix='/Data Prmission',
    tags=['Geting Data Permission'],
    responses={404:{
        'message':'Not found'
    }}
)

@router.get("/capture-screenshot")
async def capture_screenshot(urls:str,namesnap:str):
    url = urls  # Replace with your FastAPI preview server URL

    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(url)
    screenshot_path = f'{namesnap}.png'  # Replace with desired output path
    await page.screenshot({'path': screenshot_path})
    
    await browser.close()
    
    return {"message": "Screenshot captured"}

@router.post("/upload/")
async def upload_excel_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to a temporary location
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        return {"message": "File uploaded successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "An error occurred", "error": str(e)})

