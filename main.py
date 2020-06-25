""" Gather role statistics from Ansible Galaxy
"""

import asyncio
from datetime import datetime
import json
import os
import re

import aiohttp
import ansible.context
from ansible.galaxy.api import GalaxyAPI
from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import Gauge
from prometheus_client.exposition import generate_latest

# Needed for role name to role id API call
ansible.context.CLIARGS._store = {'ignore_certs': False}

if 'CACHE_SECONDS' in os.environ:
    CACHE_SECONDS = int(os.environ['CACHE_SECONDS'])
else:
    CACHE_SECONDS = 900
    fastapi_logger.info(f'Use default cache duration of {CACHE_SECONDS}s')
ANSIBLE_ROLE_URL = 'https://galaxy.ansible.com/api/v1/roles/{role_id}/?format=json'

app = FastAPI()

# Variables used for caching results
app.ROLE_NAME_TO_ID = dict()
app.LAST_FETCH = dict()
app.JDATA = dict()
app.SAFE_ROLE_NAMES = dict()
app.PMETRICS = dict()

# Root HTML page
BASE_HTML = """<html>
    <head>
        <title>Ansible Galaxy role {role_name} statistics index</title>
    </head>
    <body>
        <p>
            <a href="/role/{role_name}/metrics">Prometheus Metrics for {role_name}</a>
        </p>
        <p>
            Simple metrics for {role_name}
            <ul>
                <li>Raw <a href="/role/{role_name}/created">Created </a> epoch format datetime</li>
                <li>Raw <a href="/role/{role_name}/downloads">Download </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/forks">Forks </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/modified">Modified </a> epoch format datetime</li>
                <li>Raw <a href="/role/{role_name}/open_issues">Open Issues </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/stars">Star </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/versions">Versions </a> count integer</li>
            </ul>
        </p>
    </body>
</html>
"""
ROOT_HTML = """<html>
    <head>
        <title>Ansible Galaxy statistics index</title>
    </head>
    <body>
        <h1>Usage</h1>
        <p>
            Go to /role/{role_name}/metrics for Prometheus Metrics
        </p>
        <p>
            For simple metrics, go to:
            <ul>
                <li>/role/{role_name}/created for a raw created epoch format datetime</li>
                <li>/role/{role_name}/downloads for a raw download count integer</li>
                <li>/role/{role_name}/forks for a raw forks count integer</li>
                <li>/role/{role_name}/modified for a raw modified epoch format datetime</li>
                <li>/role/{role_name}/open_issues for a raw open issues count integer</li>
                <li>/role/{role_name}/stars for a raw stars count integer</li>
                <li>/role/{role_name}/versions for a raw version count integer</li>
            </ul>
        </p>
    </body>
</html>
"""

def ansible_role_id(role_name):
    # No asyncio... Could rewrite
    if role_name not in app.ROLE_NAME_TO_ID:
        api = GalaxyAPI(None, "test", "https://galaxy.ansible.com/api/")
        role_info = api.lookup_role_by_name(role_name, notify=False)
        app.ROLE_NAME_TO_ID[role_name] = role_info['id']
    return app.ROLE_NAME_TO_ID[role_name]

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

@app.get('/role/{role_name}', response_class=HTMLResponse)
async def role_base(role_name: str):
    """ Generate role base HTML page
    """
    return BASE_HTML.format(role_name=role_name)

@app.get("/role/{role_name}/created", response_class=PlainTextResponse)
async def role_created(role_name: str):
    return created_unixtime(await get_json(role_name))

@app.get("/role/{role_name}/downloads", response_class=PlainTextResponse)
async def role_downloads(role_name: str):
    return download_count(await get_json(role_name))

@app.get("/role/{role_name}/forks", response_class=PlainTextResponse)
async def role_forks(role_name: str):
    return fork_count(await get_json(role_name))

@app.get("/role/{role_name}/modified", response_class=PlainTextResponse)
async def role_modified(role_name: str):
    return modified_unixtime(await get_json(role_name))

@app.get("/role/{role_name}/open_issues", response_class=PlainTextResponse)
async def role_open_issues(role_name: str):
    return open_issues_count(await get_json(role_name))

@app.get("/role/{role_name}/stars", response_class=PlainTextResponse)
async def role_stars(role_name: str):
    return star_count(await get_json(role_name))

@app.get('/role/{role_name}/versions', response_class=PlainTextResponse)
async def role_versions(role_name: str):
    return version_count(await get_json(role_name))

@app.get("/role/{role_name}/metrics", response_class=PlainTextResponse)
async def metrics(role_name: str):
    role_id = ansible_role_id(role_name)
    jdata = await get_json(role_name)
    if role_name not in app.SAFE_ROLE_NAMES:
        app.SAFE_ROLE_NAMES[role_name] = re.sub('[-.]', '_', role_name)
    safe_name = app.SAFE_ROLE_NAMES[role_name]

    if role_name not in app.PMETRICS:
        # Prometheus metric definitions
        metric_prefix = f'ansible_galaxy_role_{safe_name}'
        app.PMETRICS[role_name] = dict(
            created=Gauge(f'{metric_prefix}_created', \
                'Created datetime in epoch format', ['ansible_role_name', 'ansible_role_id']),
            download=Gauge(f'{metric_prefix}_downloads', 'Download count', \
                ['ansible_role_name', 'ansible_role_id']),
            fork=Gauge(f'{metric_prefix}_forks', 'Fork count', \
                ['ansible_role_name', 'ansible_role_id']),
            modified=Gauge(f'{metric_prefix}_modified', \
                'Modified datetime in epoch format', ['ansible_role_name', 'ansible_role_id']),
            open_issues=Gauge(f'{metric_prefix}_open_issues', 'Open Issues count', \
                ['ansible_role_name', 'ansible_role_id']),
            stars=Gauge(f'{metric_prefix}_stars', 'Stars count', \
                ['ansible_role_name', 'ansible_role_id']),
            versions=Gauge(f'{metric_prefix}_versions', 'Version count', \
                ['ansible_role_name', 'ansible_role_id']),
            )
    pmetrics = app.PMETRICS[role_name]
    pmetrics['created'].labels(role_name, role_id)\
        .set(created_unixtime(jdata))
    pmetrics['download'].labels(role_name, role_id)\
        .set(download_count(jdata))
    pmetrics['fork'].labels(role_name, role_id)\
        .set(fork_count(jdata))
    pmetrics['modified'].labels(role_name, role_id)\
        .set(modified_unixtime(jdata))
    pmetrics['open_issues'].labels(role_name, role_id)\
        .set(open_issues_count(jdata))
    pmetrics['stars'].labels(role_name, role_id)\
        .set(star_count(jdata))
    pmetrics['versions'].labels(role_name, role_id)\
        .set(version_count(jdata))
    return generate_latest()

async def get_json(role_name):
    if not role_name in app.LAST_FETCH or \
        (datetime.now() - app.LAST_FETCH[role_name]).seconds > CACHE_SECONDS:
        role_id = ansible_role_id(role_name)
        fastapi_logger.info(f'Fetching "{role_name}" download count')
        # Ensure no two lookups occur at the same time
        async with asyncio.Lock():
            # Create HTTP session
            async with aiohttp.ClientSession() as session:
                # Fetch latest JSON from Ansible Galaxy API
                role_url = ANSIBLE_ROLE_URL.format(role_id=role_id)
                async with session.get(role_url) as response:
                    # Cache latest JSON
                    app.JDATA[role_name] = json.loads(await response.text())
                app.LAST_FETCH[role_name] = datetime.now()
    return app.JDATA[role_name]
