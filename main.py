""" Gather role statistics from Ansible Galaxy
"""

import asyncio
from datetime import datetime
import json
import os
import re

import aiohttp
from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import Gauge
from prometheus_client.exposition import generate_latest

# Get Ansible Role ID from environmental variable to make code generic for
# any project
ANSIBLE_ROLE_NAME = os.environ['ANSIBLE_ROLE_NAME']
ANSIBLE_ROLE_ID = os.environ['ANSIBLE_ROLE_ID']
ANSIBLE_ROLE_URL = f'https://galaxy.ansible.com/api/v1/roles/{ANSIBLE_ROLE_ID}/?format=json'
CACHE_SECONDS = int(os.environ['CACHE_SECONDS'])

# Root HTML page
ROOT_HTML = f"""<html>
    <head>
        <title>Ansible role {ANSIBLE_ROLE_NAME} statistics index</title>
    </head>
    <body>
        <p>
            <a href="/metrics">Prometheus Metrics for {ANSIBLE_ROLE_NAME}</a>
        </p>
        <p>
            Simple metrics for {ANSIBLE_ROLE_NAME}
            <ul>
                <li>Raw <a href="/created">Created </a> epoch format datetime</li>
                <li>Raw <a href="/downloads">Download </a> count integer</li>
                <li>Raw <a href="/forks">Forks </a> count integer</li>
                <li>Raw <a href="/modified">Modified </a> epoch format datetime</li>
                <li>Raw <a href="/open_issues">Open Issues </a> count integer</li>
                <li>Raw <a href="/stars">Star </a> count integer</li>
                <li>Raw <a href="/versions">Versions </a> count integer</li>
            </ul>
        </p>
    </body>
</html>
"""

# Prometheus metric definitions
ANSIBLE_ROLE_SAFE_NAME = re.sub('[-.]', '_', ANSIBLE_ROLE_NAME)
METRIC_PREFIX_TXT = f'ansible_galaxy_role_{ANSIBLE_ROLE_SAFE_NAME}'
CREATED_METRIC = Gauge(f'{METRIC_PREFIX_TXT}_created', \
    'Created datetime in epoch format', ['ansible_role_name', 'ansible_role_id'])
DOWNLOAD_METRIC = Gauge(f'{METRIC_PREFIX_TXT}_downloads', 'Download count', \
    ['ansible_role_name', 'ansible_role_id'])
FORK_METRIC = Gauge(f'{METRIC_PREFIX_TXT}_forks', 'Fork count', \
    ['ansible_role_name', 'ansible_role_id'])
MODIFIED_METRIC = Gauge(f'{METRIC_PREFIX_TXT}_modified', \
    'Modified datetime in epoch format', ['ansible_role_name', 'ansible_role_id'])
OPEN_ISSUES_METRIC = Gauge(f'{METRIC_PREFIX_TXT}_open_issues', 'Open Issues count', \
    ['ansible_role_name', 'ansible_role_id'])
STARS_METRIC = Gauge(f'{METRIC_PREFIX_TXT}_stars', 'Stars count', \
    ['ansible_role_name', 'ansible_role_id'])
VERSION_METRIC = Gauge(f'{METRIC_PREFIX_TXT}_versions', 'Version count', \
    ['ansible_role_name', 'ansible_role_id'])

app = FastAPI()

# Variables used for caching results
app.LAST_FETCH = None
app.JDATA = None

def created_unixtime(jdata):
    return str(datetime.strptime(jdata["created"], \
        '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%s'))

def download_count(jdata):
    return str(jdata["download_count"])

def fork_count(jdata):
    return str(jdata["forks_count"])

def modified_unixtime(jdata):
    return str(datetime.strptime(jdata["modified"], \
        '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%s'))

def open_issues_count(jdata):
    return str(jdata["open_issues_count"])

def star_count(jdata):
    return str(jdata["stargazers_count"])

def version_count(jdata):
    return str(len(jdata["summary_fields"]["versions"]))

@app.get("/", response_class=HTMLResponse)
async def root():
    """ Generate root HTML page
    """
    return ROOT_HTML

@app.get("/created", response_class=PlainTextResponse)
async def created():
    return created_unixtime(await get_json())

@app.get("/downloads", response_class=PlainTextResponse)
async def downloads():
    return download_count(await get_json())

@app.get("/forks", response_class=PlainTextResponse)
async def forks():
    return fork_count(await get_json())

@app.get("/modified", response_class=PlainTextResponse)
async def modified():
    return modified_unixtime(await get_json())

@app.get("/open_issues", response_class=PlainTextResponse)
async def open_issues():
    return open_issues_count(await get_json())

@app.get("/stars", response_class=PlainTextResponse)
async def stars():
    return star_count(await get_json())

@app.get("/versions", response_class=PlainTextResponse)
async def versions():
    return version_count(await get_json())

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    jdata = await get_json()
    CREATED_METRIC.labels(ANSIBLE_ROLE_NAME, ANSIBLE_ROLE_ID)\
        .set(created_unixtime(jdata))
    DOWNLOAD_METRIC.labels(ANSIBLE_ROLE_NAME, ANSIBLE_ROLE_ID)\
        .set(download_count(jdata))
    FORK_METRIC.labels(ANSIBLE_ROLE_NAME, ANSIBLE_ROLE_ID)\
        .set(fork_count(jdata))
    MODIFIED_METRIC.labels(ANSIBLE_ROLE_NAME, ANSIBLE_ROLE_ID)\
        .set(modified_unixtime(jdata))
    OPEN_ISSUES_METRIC.labels(ANSIBLE_ROLE_NAME, ANSIBLE_ROLE_ID)\
        .set(open_issues_count(jdata))
    STARS_METRIC.labels(ANSIBLE_ROLE_NAME, ANSIBLE_ROLE_ID)\
        .set(star_count(jdata))
    VERSION_METRIC.labels(ANSIBLE_ROLE_NAME, ANSIBLE_ROLE_ID)\
        .set(version_count(jdata))
    return generate_latest()

async def get_json():
    if app.JDATA is None or (datetime.now() - app.LAST_FETCH).seconds > CACHE_SECONDS:
        fastapi_logger.info(f'Fetching "{ANSIBLE_ROLE_NAME}" download count')
        # Ensure no two lookups occur at the same time
        async with asyncio.Lock():
            # Create HTTP session
            async with aiohttp.ClientSession() as session:
                # Fetch latest JSON from Ansible Galaxy API
                async with session.get(ANSIBLE_ROLE_URL) as response:
                    # Cache latest JSON
                    app.JDATA = json.loads(await response.text())
                app.LAST_FETCH = datetime.now()
    return app.JDATA
