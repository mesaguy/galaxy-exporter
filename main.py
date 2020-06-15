import json
import os

import aiohttp
import asyncio
from fastapi import FastAPI

# Get Ansible Role ID from environmental variable to make code generic for
# any project
ANSIBLE_ROLE_ID = os.environ['ANSIBLE_ROLE_ID']

app = FastAPI()

@app.get("/")
async def root():
    return await get_count(ANSIBLE_ROLE_ID)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def get_count(role):
    async with aiohttp.ClientSession() as session:
        response = await fetch(session, f'https://galaxy.ansible.com/api/v1/roles/{role}/?format=json')
        role_json = json.loads(response)
        return role_json["download_count"]
