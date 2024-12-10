import requests
import os

from supabase_client import POE_KEY

async def gpt4o(message: str):
    api_url = "https://ai.tangibly.link/bot/GPT-4o"
    apikey = POE_KEY
    params = {
        'request': message,
        'apikey': apikey
    }
    response = requests.get(api_url, params=params)
    try:
        print(f"response from gpt4o : {response}")
        jsonResponse= response.json()
        return jsonResponse
    except Exception as ex:
        print(f"JSONDecodeError???: {ex}")
    return {"error": "Error in parsing."}

async def claude35Sonnet200k(message: str):
    api_url = "https://ai.tangibly.link/call/Claude-3.5-Sonnet-200k"
    apikey = POE_KEY
    params = {
        'request': message,
        'apikey': apikey
    }
    response = requests.post(api_url, json=params)
    try:
        print(f"response from Claude-3.5-Sonnet-200k : {response}")
        jsonResponse= response.json()
        return jsonResponse
    except Exception as ex:
        print(f"JSONDecodeError???: {ex}")
    return {"error": "Error in parsing."}