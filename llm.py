import requests
import os

from supabase_client import POE_KEY

async def send_message(message: str):
    api_url = "https://ai.tangibly.link/bot/GPT-4o"
    apikey = POE_KEY
    params = {
        'request': message,
        'apikey': apikey
    }
    response = requests.get(api_url, params=params)
    try:
        print(f"response from send_message : {response}")
        jsonResponse= response.json()
        return jsonResponse
    except Exception as ex:
        print(f"JSONDecodeError???: {ex}")
    return {"error": "Error in parsing."}