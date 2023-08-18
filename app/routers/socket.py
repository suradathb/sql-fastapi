from fastapi import APIRouter,Query
from pydantic import BaseModel
import socket
import ipaddress
import requests
import subprocess
import platform

router = APIRouter(
    prefix='/Check IP Address',
    tags=['Geting IP All'],
    responses={404:{
        'message':'Not found'
    }}
)

def is_private_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False
    
def get_public_ip(ip):
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        data = response.json()
        return data["ip"]
    except requests.RequestException:
        return None

@router.get("/check_ip_by_dns/")
async def check_ip_by_dns(hostname: str):
    try:
        ip_address = socket.gethostbyname(hostname)
        return {"hostname": hostname, "ip_address": ip_address}
    except socket.gaierror as e:
        return {"error": str(e)}
    
@router.get("/check_private_ip/")
async def check_private_ip(ip: str):
    is_private = is_private_ip(ip)
    return {"ip": ip, "is_private": is_private}

@router.get("/check_ip/")
async def check_ip(ip:str):
    client_ip = ip  # You can change this to the actual client IP

    is_private = is_private_ip(client_ip)
    public_ip = get_public_ip(client_ip)
    ip_address = socket.gethostbyname(client_ip)
    if is_private:
        message = "Private IP"
    else:
        message = "Public IP"

    return {"ip": client_ip, "status": message, "public_ip": public_ip,"ip_address":ip_address}

