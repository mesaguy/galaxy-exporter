""" Gather role statistics from Ansible Galaxy
"""

import asyncio
from datetime import datetime
import json
import os
import re

import aiohttp
from dateutil.parser import parse as dateparse
from fastapi import FastAPI, HTTPException
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import CollectorRegistry, Counter, Gauge, Info
from prometheus_client.exposition import generate_latest

from galaxy_exporter import __version__

if 'CACHE_SECONDS' in os.environ:
    CACHE_SECONDS = int(os.environ['CACHE_SECONDS'])
else:
    CACHE_SECONDS = 15

app = FastAPI()

# Variables used for caching results
METRICS = dict()
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
                <li>Raw <a href="/collection/{collection_name}/community_score">Community score </a> count</li>
                <li>Raw <a href="/collection/{collection_name}/community_surveys">Community surveys</a> count</li>
                <li>Raw <a href="/collection/{collection_name}/created">Created </a> epoch format datetime</li>
                <li>Raw <a href="/collection/{collection_name}/dependencies">Dependencies </a> count</li>
                <li>Raw <a href="/collection/{collection_name}/downloads">Download </a> count</li>
                <li>Raw <a href="/collection/{collection_name}/modified">Modified </a> epoch format datetime</li>
                <li>Raw <a href="/collection/{collection_name}/quality_score">Quality score </a> count</li>
                <li>Raw <a href="/collection/{collection_name}/version">Version </a> current version</li>
                <li>Raw <a href="/collection/{collection_name}/versions">Versions </a> count</li>
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
                <li>Raw <a href="/role/{role_name}/community_score">Community score </a> count</li>
                <li>Raw <a href="/role/{role_name}/community_surveys">Community surveys</a> count</li>
                <li>Raw <a href="/role/{role_name}/created">Created </a> epoch format datetime</li>
                <li>Raw <a href="/role/{role_name}/downloads">Download </a> count</li>
                <li>Raw <a href="/role/{role_name}/forks">Forks </a> count</li>
                <li>Raw <a href="/role/{role_name}/imported">Imported </a> epoch format datetime</li>
                <li>Raw <a href="/role/{role_name}/modified">Modified </a> epoch format datetime</li>
                <li>Raw <a href="/role/{role_name}/open_issues">Open Issues </a> count</li>
                <li>Raw <a href="/role/{role_name}/quality_score">Quality score </a> count</li>
                <li>Raw <a href="/role/{role_name}/stars">Star </a> count</li>
                <li>Raw <a href="/role/{role_name}/version">Version </a> current version</li>
                <li>Raw <a href="/role/{role_name}/versions">Versions </a> count</li>
                <li>Raw <a href="/role/{role_name}/watchers">Watcher </a> count</li>
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
                <li>/role/ROLE_NAME/community_score for a raw community score count</li>
                <li>/role/ROLE_NAME/community_surveys for a raw community survey count</li>
                <li>/role/ROLE_NAME/created for a raw created datetime in epoch format</li>
                <li>/role/ROLE_NAME/downloads for a raw download count</li>
                <li>/role/ROLE_NAME/forks for a raw forks count</li>
                <li>/role/ROLE_NAME/imported for a raw imported datetime in epoch format</li>
                <li>/role/ROLE_NAME/modified for a raw modified datetime in epoch format</li>
                <li>/role/ROLE_NAME/open_issues for a raw open issues count</li>
                <li>/role/ROLE_NAME/quality_score for a raw quality score count</li>
                <li>/role/ROLE_NAME/stars for a raw stars count</li>
                <li>/role/ROLE_NAME/version for a raw version number</li>
                <li>/role/ROLE_NAME/versions for a raw version count</li>
                <li>/role/ROLE_NAME/watchers for a raw watcher count</li>
            </ul>
        </p>
        <p>
            Go to /role/COLLECTION_NAME/metrics for Prometheus Metrics
        </p>
        <p>
            For simple metrics, go to:
            <ul>
                <li>/role/COLLECTION_NAME/community_score for a raw community score count</li>
                <li>/role/COLLECTION_NAME/community_surveys for a raw community survey count</li>
                <li>/role/COLLECTION_NAME/created for a raw created datetime in epoch format</li>
                <li>/role/COLLECTION_NAME/dependencies for a raw dependency count</li>
                <li>/role/COLLECTION_NAME/downloads for a raw download count</li>
                <li>/role/COLLECTION_NAME/modified for a raw modified datetime in epoch format</li>
                <li>/role/COLLECTION_NAME/quality_score for a raw quality score count</li>
                <li>/role/COLLECTION_NAME/version for a raw version number</li>
                <li>/role/COLLECTION_NAME/versions for a raw version count</li>
            </ul>
        </p>
    </body>
</html>
"""


class GalaxyData:
    def __init__(self, name):
        self.name = name
        self.registry = CollectorRegistry()
        self.metrics = self._setup_metrics()
        self.data = dict()
        self.last_update = None

    def _setup_metrics(self):
        """ Placeholder
        """
        return dict()

    def url(self):
        """ Placeholder
        """
        return None

    def _setup_generic_metrics(self, metric_prefix, labels):
        return dict(
            created=Gauge(f'{metric_prefix}created',
                          'Created datetime in epoch format', labels,
                          registry=self.registry),
            community_score=Gauge(f'{metric_prefix}community_score',
                                  'Community score', labels,
                                  registry=self.registry),
            community_survey=Gauge(f'{metric_prefix}community_surveys',
                                   'Community surveys', labels,
                                   registry=self.registry),
            download=Gauge(f'{metric_prefix}downloads', 'Download count',
                           labels, registry=self.registry),
            modified=Gauge(f'{metric_prefix}modified',
                           'Modified datetime in epoch format', labels,
                           registry=self.registry),
            quality_score=Gauge(f'{metric_prefix}quality_score', 'Quality score',
                                labels, registry=self.registry),
            version=Info(f'{metric_prefix}version', 'Current release version',
                         registry=self.registry),
            versions=Gauge(f'{metric_prefix}versions', 'Version count',
                           labels, registry=self.registry),
        )

    def metric__community_score(self):
        score = self.data['community_score']
        if score is None:
            return '0'
        return str(score)

    def metric__community_surveys(self):
        return str(self.data['community_survey_count'])

    def metric__created(self):
        return str(dateparse(self.data['created']).strftime('%s'))

    def metric__downloads(self):
        return str(self.data['download_count'])

    def metric__modified(self):
        return str(dateparse(self.data['modified']).strftime('%s'))

    async def update(self):
        fastapi_logger.info('Fetching %s "%s" metadata', self.__class__.__name__, self.name)
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

    def needs_update(self, cache_seconds=CACHE_SECONDS):
        if self.last_update is None:
            return True
        if (datetime.now() - self.last_update).seconds > cache_seconds:
            return True
        return False


class Collection(GalaxyData):
    def __init__(self, name):
        self.author, self.collection = name.split('.', 2)
        super().__init__(name)

    def metric__dependencies(self):
        return str(len(self.data['latest_version']['metadata']['dependencies']))

    def metric__quality_score(self):
        score = self.data['latest_version']['quality_score']
        if score is None:
            return '0'
        return str(score)

    def url(self):
        return 'https://galaxy.ansible.com/api/internal/ui/collections/' \
            f'{self.author}/{self.collection}/?format=json'

    def metric__version(self):
        return self.data['latest_version']['version']

    def metric__versions(self):
        return str(len(self.data['all_versions']))

    def _setup_metrics(self):
        metric_prefix = 'ansible_galaxy_collection_'
        metrics = self._setup_generic_metrics(metric_prefix, ['job', 'instance'])
        metrics.update(dict(
            dependency=Gauge(f'{metric_prefix}dependencies', 'Dependency count',
                             ['job', 'instance'], registry=self.registry),
            ))
        return metrics


class Role(GalaxyData):
    def __init__(self, name):
        self.author, self.role = name.split('.', 2)
        super().__init__(name)

    def url(self):
        return 'https://galaxy.ansible.com/api/internal/ui/' \
            'repo-or-collection-detail/?format=json&namespace=' \
            f'{self.author}&name={self.role}'

    def _setup_metrics(self):
        metric_prefix = 'ansible_galaxy_role_'
        metrics = self._setup_generic_metrics(metric_prefix, ['job', 'instance'])
        metrics.update(dict(
            fork=Gauge(f'{metric_prefix}forks', 'Fork count', ['job', 'instance'],
                       registry=self.registry),
            imported=Gauge(f'{metric_prefix}imported',
                           'Imported datetime in epoch format', ['job', 'instance'],
                           registry=self.registry),
            open_issue=Gauge(f'{metric_prefix}open_issues',
                             'Open Issues count', ['job', 'instance'],
                             registry=self.registry),
            star=Gauge(f'{metric_prefix}stars', 'Stars count',
                       ['job', 'instance'], registry=self.registry),
            watchers=Gauge(f'{metric_prefix}watchers', 'Watcher count',
                           ['job', 'instance'], registry=self.registry),
            ))
        return metrics

    def metric__quality_score(self):
        score = self.data['quality_score']
        if score is None:
            return '0'
        return str(score)

    def metric__forks(self):
        return str(self.data['forks_count'])

    def metric__imported(self):
        return str(dateparse(self.data['summary_fields']['latest_import']\
                   ['finished']).strftime('%s'))

    def metric__open_issues(self):
        return str(self.data['open_issues_count'])

    def metric__stars(self):
        return str(self.data['stargazers_count'])

    def metric__watchers(self):
        return str(self.data['watchers_count'])

    def metric__version(self):
        return self.data['summary_fields']['versions'][0]['version']

    def metric__versions(self):
        return str(len(self.data['summary_fields']['versions']))


def set_collection_metrics(collection):
    collection.metrics['community_score'].labels('galaxy', collection.name)\
        .set(collection.metric__community_score())
    collection.metrics['community_survey'].labels('galaxy', collection.name)\
        .set(collection.metric__community_surveys())
    collection.metrics['created'].labels('galaxy', collection.name).set(collection.metric__created())
    collection.metrics['dependency'].labels('galaxy', collection.name).set(collection.metric__dependencies())
    collection.metrics['download'].labels('galaxy', collection.name).set(collection.metric__downloads())
    collection.metrics['modified'].labels('galaxy', collection.name).set(collection.metric__modified())
    collection.metrics['quality_score'].labels('galaxy', collection.name)\
        .set(collection.metric__quality_score())
    collection.metrics['version'].info({'version': collection.metric__version()})
    collection.metrics['versions'].labels('galaxy', collection.name).set(collection.metric__versions())
    return collection


def set_role_metrics(role):
    role.metrics['community_score'].labels('galaxy', role.name).set(role.metric__community_score())
    role.metrics['community_survey'].labels('galaxy', role.name).set(role.metric__community_surveys())
    role.metrics['created'].labels('galaxy', role.name).set(role.metric__created())
    role.metrics['download'].labels('galaxy', role.name).set(role.metric__downloads())
    role.metrics['fork'].labels('galaxy', role.name).set(role.metric__forks())
    role.metrics['imported'].labels('galaxy', role.name).set(role.metric__imported())
    role.metrics['modified'].labels('galaxy', role.name).set(role.metric__modified())
    role.metrics['open_issue'].labels('galaxy', role.name).set(role.metric__open_issues())
    role.metrics['quality_score'].labels('galaxy', role.name).set(role.metric__quality_score())
    role.metrics['star'].labels('galaxy', role.name).set(role.metric__stars())
    role.metrics['version'].info({'version': role.metric__version()})
    role.metrics['versions'].labels('galaxy', role.name).set(role.metric__versions())
    role.metrics['watchers'].labels('galaxy', role.name).set(role.metric__watchers())
    return role


@app.get("/", response_class=HTMLResponse)
async def root():
    """ Generate root HTML page
    """
    return ROOT_HTML


@app.get("/metrics", response_class=PlainTextResponse)
async def process_metrics():
    update_base_metrics()
    return generate_latest()


@app.get('/collection/{collection_name}', response_class=HTMLResponse)
async def collection_base(collection_name: str):
    """ Generate collection base HTML page
    """
    return COLLECTION_HTML.format(collection_name=collection_name)


@app.get('/probe', response_class=PlainTextResponse)
async def probe(module: str, target: str):
    if module not in ['collection', 'role']:
        raise HTTPException(status_code=404,
                            detail=f'Unknown module {module}, use '
                            '"collection" or "role"')
    if module == 'collection':
        collection = await get_collection(target)
        collection = set_collection_metrics(collection)
        return generate_latest(registry=collection.registry)
    role = await get_role(target)
    role = set_role_metrics(role)
    return generate_latest(registry=role.registry)


@app.get('/collection/{collection_name}/{metric}', response_class=PlainTextResponse)
async def collection_community_score(collection_name: str, metric: str):
    collection = await get_collection(collection_name)
    if metric == 'metrics':
        collection = set_collection_metrics(collection)
        return generate_latest(registry=collection.registry)
    return getattr(collection, f'metric__{metric}')()


@app.get('/role/{role_name}', response_class=HTMLResponse)
async def role_base(role_name: str):
    """ Generate role base HTML page
    """
    return ROLE_HTML.format(role_name=role_name)


@app.get('/role/{role_name}/{metric}', response_class=PlainTextResponse)
async def role_community_score(role_name: str, metric: str):
    role = await get_role(role_name)
    if metric == 'metrics':
        role = set_role_metrics(role)
        return generate_latest(registry=role.registry)
    return getattr(role, f'metric__{metric}')()


def update_base_metrics(increment=False):
    if 'version' not in METRICS:
        METRICS['version'] = Info(f'ansible_galaxy_exporter_version',
            'Current exporter version')
        METRICS['version'].info({'version': __version__})
    if 'api_call_count' not in METRICS:
        METRICS['api_call_count'] = Counter('ansible_galaxy_exporter_api_call_count',
            'API calls to Ansible Galaxy')
    if increment:
        METRICS['api_call_count'].inc()


async def get_collection(collection_name):
    update_base_metrics(increment=True)
    if collection_name not in COLLECTIONS:
        COLLECTIONS[collection_name] = Collection(collection_name)
    collection = COLLECTIONS[collection_name]
    if collection.needs_update():
        data = await collection.update()
        collection.data = data
    return collection


async def get_role(role_name):
    update_base_metrics(increment=True)
    if role_name not in ROLES:
        ROLES[role_name] = Role(role_name)
    role = ROLES[role_name]
    if role.needs_update():
        data = await role.update()
        role.data = data['data']['repository']
    return role
