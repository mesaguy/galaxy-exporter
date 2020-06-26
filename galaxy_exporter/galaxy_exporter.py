""" Gather role statistics from Ansible Galaxy
"""

import asyncio
from datetime import datetime
import json
import os
import re

import aiohttp
from dateutil.parser import parse as dateparse
from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import CollectorRegistry, Gauge, Info
from prometheus_client.exposition import generate_latest

from galaxy_exporter import __version__

if 'CACHE_SECONDS' in os.environ:
    CACHE_SECONDS = int(os.environ['CACHE_SECONDS'])
else:
    CACHE_SECONDS = 15

app = FastAPI()

# Variables used for caching results
ROLES = dict()
COLLECTIONS = dict()

# Root Collection HTML page
COLLECTION_HTML = """<html>
    <head>
        <title>Ansible Galaxy collection {collection_name} statistics index</title>
    </head>
    <body>
        <p>
            <a href="/collection/{collection_name}/metrics">Prometheus Metrics for {collection_name}</a>
        </p>
        <p>
            Simple metrics for {collection_name}
            <ul>
                <li>Raw <a href="/collection/{collection_name}/community_score">Community score </a> count integer</li>
                <li>Raw <a href="/collection/{collection_name}/community_surveys">Community surveys</a> count integer</li>
                <li>Raw <a href="/collection/{collection_name}/created">Created </a> epoch format datetime</li>
                <li>Raw <a href="/collection/{collection_name}/dependencies">Dependencies </a> count integer</li>
                <li>Raw <a href="/collection/{collection_name}/downloads">Download </a> count integer</li>
                <li>Raw <a href="/collection/{collection_name}/modified">Modified </a> epoch format datetime</li>
                <li>Raw <a href="/collection/{collection_name}/quality_score">Quality score </a> count integer</li>
                <li>Raw <a href="/collection/{collection_name}/version">Version </a> current version</li>
                <li>Raw <a href="/collection/{collection_name}/versions">Versions </a> count integer</li>
            </ul>
        </p>
    </body>
</html>
"""
# Root Role HTML page
ROLE_HTML = """<html>
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
                <li>Raw <a href="/role/{role_name}/community_score">Community score </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/community_surveys">Community surveys</a> count integer</li>
                <li>Raw <a href="/role/{role_name}/created">Created </a> epoch format datetime</li>
                <li>Raw <a href="/role/{role_name}/dependencies">Dependencies </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/downloads">Download </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/forks">Forks </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/imported">Imported </a> epoch format datetime</li>
                <li>Raw <a href="/role/{role_name}/modified">Modified </a> epoch format datetime</li>
                <li>Raw <a href="/role/{role_name}/open_issues">Open Issues </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/platforms">Platforms </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/quality_score">Quality score </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/stars">Star </a> count integer</li>
                <li>Raw <a href="/role/{role_name}/version">Version </a> current version</li>
                <li>Raw <a href="/role/{role_name}/versions">Versions </a> count integer</li>
            </ul>
        </p>
    </body>
</html>
"""

RE_SAFE = re.compile('[-.]')
ROOT_HTML = f"""<html>
    <head>
        <title>Ansible Galaxy Exporter v{__version__} statistics index</title>
    </head>
    <body>
        <h1>Usage</h1>
        <p>
            <a href="/metrics">Prometheus exporter process metrics</a>
        </p>
        <p>
        All role and collection names must be in the format for AUTHOR.ROLE or AUTHOR.COLLECTION
        </p>
        <p>
            Go to /role/ROLE_NAME/metrics for Prometheus Metrics
        </p>
        <p>
            For simple metrics, go to:
            <ul>
                <li>/role/ROLE_NAME/community_score for a raw community score count float</li>
                <li>/role/ROLE_NAME/community_surveys for a raw community survey count integer</li>
                <li>/role/ROLE_NAME/created for a raw created datetime in epoch format</li>
                <li>/role/ROLE_NAME/dependencies for a raw dependency count integer</li>
                <li>/role/ROLE_NAME/downloads for a raw download count integer</li>
                <li>/role/ROLE_NAME/forks for a raw forks count integer</li>
                <li>/role/ROLE_NAME/imported for a raw imported datetime in epoch format</li>
                <li>/role/ROLE_NAME/modified for a raw modified datetime in epoch format</li>
                <li>/role/ROLE_NAME/open_issues for a raw open issues count integer</li>
                <li>/role/ROLE_NAME/platforms for a raw platform count integer</li>
                <li>/role/ROLE_NAME/quality_score for a raw quality score count float</li>
                <li>/role/ROLE_NAME/stars for a raw stars count integer</li>
                <li>/role/ROLE_NAME/version for a raw version number</li>
                <li>/role/ROLE_NAME/versions for a raw version count integer</li>
            </ul>
        </p>
        <p>
            Go to /role/COLLECTION_NAME/metrics for Prometheus Metrics
        </p>
        <p>
            For simple metrics, go to:
            <ul>
                <li>/role/COLLECTION_NAME/community_score for a raw community score count float</li>
                <li>/role/COLLECTION_NAME/community_surveys for a raw community survey count integer</li>
                <li>/role/COLLECTION_NAME/created for a raw created datetime in epoch format</li>
                <li>/role/COLLECTION_NAME/dependencies for a raw dependency count integer</li>
                <li>/role/COLLECTION_NAME/downloads for a raw download count integer</li>
                <li>/role/COLLECTION_NAME/modified for a raw modified datetime in epoch format</li>
                <li>/role/COLLECTION_NAME/quality_score for a raw quality score count float</li>
                <li>/role/COLLECTION_NAME/version for a raw version number</li>
                <li>/role/COLLECTION_NAME/versions for a raw version count integer</li>
            </ul>
        </p>
    </body>
</html>
"""

class GalaxyData:
    def __init__(self, name):
        self.author, self.name = name.split('.', 2)
        self.registry = CollectorRegistry()
        self.metrics = self._setup_metrics()
        self.data = dict()
        self.last_update = None

    def _setup_metrics(self):
        """ Placeholder
        """
        return dict()

    def _setup_generic_metrics(self, metric_prefix, labels):
        return dict(
            created=Gauge(f'{metric_prefix}_created', \
                'Created datetime in epoch format', labels, \
                registry=self.registry),
            community_score=Gauge(f'{metric_prefix}_community_score', 'Community score', \
                labels, registry=self.registry),
            community_survey=Gauge(f'{metric_prefix}_community_surveys', 'Community surveys', \
                labels, registry=self.registry),
            dependency=Gauge(f'{metric_prefix}_dependencies', 'Dependency count', \
                labels, registry=self.registry),
            download=Gauge(f'{metric_prefix}_downloads', 'Download count', \
                labels, registry=self.registry),
            modified=Gauge(f'{metric_prefix}_modified', \
                'Modified datetime in epoch format', labels, \
                registry=self.registry),
            quality_score=Gauge(f'{metric_prefix}_quality_score', 'Quality score', \
                labels, registry=self.registry),
            version=Info(f'{metric_prefix}_version', 'Current release version',
                registry=self.registry),
            versions=Gauge(f'{metric_prefix}_versions', 'Version count', \
                labels, registry=self.registry),
        )

    def created_epoch(self):
        return str(dateparse(self.data['created']).strftime('%s'))

    def downloads(self):
        return str(self.data['download_count'])

    def modified_epoch(self):
        return str(dateparse(self.data['modified']).strftime('%s'))

    def full_name(self):
        return f'{self.author}.{self.name}'

    def safe_name(self):
        return RE_SAFE.sub('_', self.full_name())

    async def update(self):
        fastapi_logger.info('Fetching %s "%s" metadata',
            self.__class__.__name__, self.full_name())
        # Ensure no two lookups occur at the same time
        async with asyncio.Lock():
            # Create HTTP session
            async with aiohttp.ClientSession() as session:
                # Fetch latest JSON from Ansible Galaxy API
                async with session.get(self.url()) as response:
                    # Cache latest JSON
                    jdata = json.loads(await response.text())
        self.last_update = datetime.now()
        return jdata

    def needs_update(self):
        if self.last_update is None:
            return True
        if (datetime.now() - self.last_update).seconds > CACHE_SECONDS:
            return True
        return False

class Collection(GalaxyData):
    def community_score(self):
        score = self.data['community_score']
        if score is None:
            return '0'
        return str(score)

    def community_surveys(self):
        return str(self.data['community_survey_count'])

    def dependencies(self):
        return str(len(self.data['latest_version']['metadata']['dependencies']))

    def quality_score(self):
        score = self.data['latest_version']['quality_score']
        if score is None:
            return '0'
        return str(score)

    def url(self):
        return 'https://galaxy.ansible.com/api/internal/ui/collections/' \
            f'{self.author}/{self.name}/?format=json'

    def version(self):
        return self.data['latest_version']['version']

    def versions(self):
        return str(len(self.data['all_versions']))

    def _setup_metrics(self):
        metric_prefix = f'ansible_galaxy_collection_{self.safe_name()}'
        metrics = self._setup_generic_metrics(metric_prefix, ['collection_name'])
        return metrics

class Role(GalaxyData):
    def url(self):
        return 'https://galaxy.ansible.com/api/v1/roles/?' \
            f'owner__username={self.author}&name={self.name}'

    def _setup_metrics(self):
        metric_prefix = f'ansible_galaxy_role_{self.safe_name()}'
        metrics = self._setup_generic_metrics(metric_prefix, ['role_name'])
        metrics.update(dict(
            fork=Gauge(f'{metric_prefix}_forks', 'Fork count', \
                ['role_name'], registry=self.registry),
            imported=Gauge(f'{metric_prefix}_imported', \
                'Imported datetime in epoch format', ['role_name'], \
                registry=self.registry),
            platform=Gauge(f'{metric_prefix}_platforms', 'Platform count', \
                ['role_name'], registry=self.registry),
            open_issue=Gauge(f'{metric_prefix}_open_issues', \
                'Open Issues count', ['role_name'], registry=self.registry),
            star=Gauge(f'{metric_prefix}_stars', 'Stars count', \
                ['role_name'], registry=self.registry),
            ))
        return metrics

    def community_score(self):
        score = self.data['summary_fields']['repository']['community_score']
        if score is None:
            return '0'
        return str(score)

    def dependencies(self):
        return str(len(self.data['summary_fields']['dependencies']))

    def platforms(self):
        return str(len(self.data['summary_fields']['platforms']))

    def quality_score(self):
        score = self.data['summary_fields']['repository']['quality_score']
        if score is None:
            return '0'
        return str(score)

    def community_surveys(self):
        return str(self.data['summary_fields']['repository']['community_survey_count'])

    def forks(self):
        return str(self.data['forks_count'])

    def imported_epoch(self):
        return str(dateparse(self.data['imported']).strftime('%s'))

    def open_issues(self):
        return str(self.data['open_issues_count'])

    def stars(self):
        return str(self.data['stargazers_count'])

    def version(self):
        return self.data['summary_fields']['versions'][0]["name"]

    def versions(self):
        return str(len(self.data['summary_fields']['versions']))

@app.get("/", response_class=HTMLResponse)
async def root():
    """ Generate root HTML page
    """
    return ROOT_HTML

@app.get("/metrics", response_class=PlainTextResponse)
async def process_metrics():
    return generate_latest()

@app.get('/collection/{collection_name}', response_class=HTMLResponse)
async def role_base(collection_name: str):
    """ Generate collection base HTML page
    """
    return COLLECTION_HTML.format(collection_name=collection_name)

@app.get('/collection/{collection_name}/community_score', response_class=PlainTextResponse)
async def collection_community_score(collection_name: str):
    collection = await get_collection(collection_name)
    return collection.community_score()

@app.get('/collection/{collection_name}/community_surveys', response_class=PlainTextResponse)
async def collection_community_surveys(collection_name: str):
    collection = await get_collection(collection_name)
    return collection.community_surveys()

@app.get("/collection/{collection_name}/created", response_class=PlainTextResponse)
async def collection_created(collection_name: str):
    collection = await get_collection(collection_name)
    return collection.created_epoch()

@app.get('/collection/{collection_name}/dependencies', response_class=PlainTextResponse)
async def collection_dependencies(collection_name: str):
    collection = await get_collection(collection_name)
    return collection.dependencies()

@app.get("/collection/{collection_name}/downloads", response_class=PlainTextResponse)
async def collection_downloads(collection_name: str):
    collection = await get_collection(collection_name)
    return collection.downloads()

@app.get("/collection/{collection_name}/modified", response_class=PlainTextResponse)
async def collection_modified(collection_name: str):
    collection = await get_collection(collection_name)
    return collection.modified_epoch()

@app.get('/collection/{collection_name}/quality_score', response_class=PlainTextResponse)
async def collection_quality_score(collection_name: str):
    collection = await get_collection(collection_name)
    return collection.quality_score()

@app.get('/collection/{collection_name}/version', response_class=PlainTextResponse)
async def collection_version(collection_name: str):
    collection = await get_collection(collection_name)
    return collection.version()

@app.get('/collection/{collection_name}/versions', response_class=PlainTextResponse)
async def collection_versions(collection_name: str):
    collection = await get_collection(collection_name)
    return collection.versions()

@app.get("/collection/{collection_name}/metrics", response_class=PlainTextResponse)
async def metrics(collection_name: str):
    collection = await get_collection(collection_name)
    collection.metrics['community_score'].labels(collection_name).set(collection.community_score())
    collection.metrics['community_survey'].labels(collection_name).set(collection.community_surveys())
    collection.metrics['created'].labels(collection_name).set(collection.created_epoch())
    collection.metrics['dependency'].labels(collection_name).set(collection.dependencies())
    collection.metrics['download'].labels(collection_name).set(collection.downloads())
    collection.metrics['modified'].labels(collection_name).set(collection.modified_epoch())
    collection.metrics['quality_score'].labels(collection_name).set(collection.quality_score())
    collection.metrics['version'].info({'version': collection.version()})
    collection.metrics['versions'].labels(collection_name).set(collection.versions())
    return generate_latest(registry=collection.registry)

@app.get('/role/{role_name}', response_class=HTMLResponse)
async def role_base(role_name: str):
    """ Generate role base HTML page
    """
    return ROLE_HTML.format(role_name=role_name)

@app.get('/role/{role_name}/community_score', response_class=PlainTextResponse)
async def role_community_score(role_name: str):
    role = await get_role(role_name)
    return role.community_score()

@app.get('/role/{role_name}/community_surveys', response_class=PlainTextResponse)
async def role_community_surveys(role_name: str):
    role = await get_role(role_name)
    return role.community_surveys()

@app.get("/role/{role_name}/created", response_class=PlainTextResponse)
async def role_created(role_name: str):
    role = await get_role(role_name)
    return role.created_epoch()

@app.get('/role/{role_name}/dependencies', response_class=PlainTextResponse)
async def role_dependencies(role_name: str):
    role = await get_role(role_name)
    return role.dependencies()

@app.get("/role/{role_name}/downloads", response_class=PlainTextResponse)
async def role_downloads(role_name: str):
    role = await get_role(role_name)
    return role.downloads()

@app.get("/role/{role_name}/forks", response_class=PlainTextResponse)
async def role_forks(role_name: str):
    role = await get_role(role_name)
    return role.forks()

@app.get("/role/{role_name}/imported", response_class=PlainTextResponse)
async def role_imported(role_name: str):
    role = await get_role(role_name)
    return role.imported_epoch()

@app.get("/role/{role_name}/modified", response_class=PlainTextResponse)
async def role_modified(role_name: str):
    role = await get_role(role_name)
    return role.modified_epoch()

@app.get('/role/{role_name}/platforms', response_class=PlainTextResponse)
async def role_platforms(role_name: str):
    role = await get_role(role_name)
    return role.platforms()

@app.get('/role/{role_name}/quality_score', response_class=PlainTextResponse)
async def role_quality_score(role_name: str):
    role = await get_role(role_name)
    return role.quality_score()

@app.get("/role/{role_name}/open_issues", response_class=PlainTextResponse)
async def role_open_issues(role_name: str):
    role = await get_role(role_name)
    return role.open_issues()

@app.get("/role/{role_name}/stars", response_class=PlainTextResponse)
async def role_stars(role_name: str):
    role = await get_role(role_name)
    return role.stars()

@app.get('/role/{role_name}/version', response_class=PlainTextResponse)
async def role_version(role_name: str):
    role = await get_role(role_name)
    return role.version()

@app.get('/role/{role_name}/versions', response_class=PlainTextResponse)
async def role_versions(role_name: str):
    role = await get_role(role_name)
    return role.versions()

@app.get("/role/{role_name}/metrics", response_class=PlainTextResponse)
async def metrics(role_name: str):
    role = await get_role(role_name)
    role.metrics['community_score'].labels(role_name).set(role.community_score())
    role.metrics['community_survey'].labels(role_name).set(role.community_surveys())
    role.metrics['created'].labels(role_name).set(role.created_epoch())
    role.metrics['dependency'].labels(role_name).set(role.dependencies())
    role.metrics['download'].labels(role_name).set(role.downloads())
    role.metrics['fork'].labels(role_name).set(role.forks())
    role.metrics['imported'].labels(role_name).set(role.imported_epoch())
    role.metrics['modified'].labels(role_name).set(role.modified_epoch())
    role.metrics['open_issue'].labels(role_name).set(role.open_issues())
    role.metrics['platform'].labels(role_name).set(role.platforms())
    role.metrics['quality_score'].labels(role_name).set(role.quality_score())
    role.metrics['star'].labels(role_name).set(role.stars())
    role.metrics['version'].info({'version': role.version()})
    role.metrics['versions'].labels(role_name).set(role.versions())
    return generate_latest(registry=role.registry)

async def get_collection(collection_name):
    if not collection_name in COLLECTIONS:
        COLLECTIONS[collection_name] = Collection(collection_name)
    collection = COLLECTIONS[collection_name]
    if collection.needs_update():
        data = await collection.update()
        collection.data = data
    return collection

async def get_role(role_name):
    if not role_name in ROLES:
        ROLES[role_name] = Role(role_name)
    role = ROLES[role_name]
    if role.needs_update():
        data = await role.update()
        role.data = data["results"][0]
    return role
