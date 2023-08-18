from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import asyncio
from pyppeteer import launch


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