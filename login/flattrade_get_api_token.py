import httpx
import pyotp
import asyncio
import hashlib
import logging
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO)

'''
###############################################################
---------------Enter Your Credentials Below--------------------
###############################################################
'''
USER = "" # Flattrade user id
PWD = "" # Password
TOTP_KEY = ""
API_KEY = ""
API_SECRET = ""
RURL = "https://127.0.0.1:5000/?"

###############################################################

HOST = "https://auth.flattrade.in"
API_HOST = "https://authapi.flattrade.in"

routes = {
    "session" : f"{API_HOST}/auth/session",
    "ftauth" : f"{API_HOST}/ftauth",
    "apitoken" : f"{API_HOST}/trade/apitoken",
}

headers = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Host": "authapi.flattrade.in",
    "Origin": f"{HOST}",
    "Referer": f"{HOST}/",
}

def encode_item(item):
    encoded_item = hashlib.sha256(item.encode()).hexdigest() 
    return encoded_item

async def get_authcode():

    async with httpx.AsyncClient(http2= True, headers= headers) as client:
        response =  await client.post(
                routes["session"]
            )
        if response.status_code == 200:
            sid = response.text

            response =  await client.post(
                routes["ftauth"],
                json = {
                        "UserName": USER,
                        "Password": encode_item(PWD),
                        "App":"",
                        "ClientID":"",
                        "Key":"",
                        "APIKey": API_KEY,
                        "PAN_DOB": pyotp.TOTP(TOTP_KEY).now(),
                        "Sid" : sid
                        }
                    )    
            
            if response.status_code == 200:
                redirect_url = response.json().get("RedirectURL", "")

                query_params = parse_qs(urlparse(redirect_url).query)
                if 'code' in query_params:
                    code = query_params['code'][0]
                    logging.info(code)
                    return code
            else:
                logging.info(response.json())
        else:
            logging.info(response.text)

async def get_apitoken(code):
    async with httpx.AsyncClient(http2= True) as client:
        response = await client.post(
            routes["apitoken"],
            json = {
                "api_key": API_KEY,
                "request_code": code, 
                "api_secret": encode_item(f"{API_KEY}{code}{API_SECRET}")
                }
            )
        
        if response.status_code == 200:
            token = response.json().get("token", "")
            return token
        else:
            logging.info(response.json())

if __name__ == "__main__":

    code = asyncio.run(get_authcode())
    token = asyncio.run(get_apitoken(code))
    print(token)
