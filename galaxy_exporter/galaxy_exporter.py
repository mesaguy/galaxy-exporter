""" Gather role statistics from Ansible Galaxy
"""

# pylint: disable=R0201

import asyncio
from datetime import datetime
import json
import os
import re
from typing import Dict, Optional

import aiohttp
from dateutil.parser import parse as dateparse
from fastapi import FastAPI, HTTPException
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import CollectorRegistry  # type: ignore
from prometheus_client import Counter, Gauge, Info
from prometheus_client.exposition import generate_latest  # type: ignore
from tenacity import AsyncRetrying, RetryError, stop_after_delay

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
    """Base class for storing Ansible Galaxy data.

    Args:
        name (str): Full name of collection or role.

    Attributes:
        name (str): Full name of collection or role.
        labels (dict): Mappings of Prometheus label names to label values
        registry (prometheus_client.CollectorRegistry): Instance of Prometheus
            client 'CollectorRegistry' for storing metrics
        data (dict): Raw json data from Ansible Galaxy regarding collection or role
        metrics (dict): Maps str names of Prometheus metrics to Prometheus client
            metric instances
        last_update (datetime): Datetime of last time Galaxy data was fetched
    """
    def __init__(self, name: str) -> None:
        self.name = name
        if not hasattr(self, 'labels'):
            self.labels: Dict[str, str] = dict()
        self.registry = CollectorRegistry()
        self.metrics = self._setup_metrics()
        self.data: Dict[str, str] = dict()
        self.last_update = None

    def _setup_metrics(self):
        """ Placeholder to be overridden by inheriting classes
        """
        return dict()

    def url(self) -> Optional[str]:
        """ Placeholder to be overridden by inheriting classes
        """
        return None

    def _setup_generic_metrics(self, metric_prefix: str) -> dict:
        return dict(
            created=Gauge(f'{metric_prefix}created',
                          'Created datetime in epoch format',
                          self.labels.keys(), registry=self.registry),
            community_score=Gauge(f'{metric_prefix}community_score',
                                  'Community score',
                                  self.labels.keys(), registry=self.registry),
            community_survey=Gauge(f'{metric_prefix}community_surveys',
                                   'Community surveys',
                                   self.labels.keys(), registry=self.registry),
            download=Gauge(f'{metric_prefix}downloads', 'Download count',
                           self.labels.keys(), registry=self.registry),
            modified=Gauge(f'{metric_prefix}modified',
                           'Modified datetime in epoch format',
                           self.labels.keys(), registry=self.registry),
            quality_score=Gauge(f'{metric_prefix}quality_score', 'Quality score',
                                self.labels.keys(), registry=self.registry),
            version=Info(f'{metric_prefix}version', 'Current release version',
                         self.labels.keys(), registry=self.registry),
            versions=Gauge(f'{metric_prefix}versions', 'Version count',
                           self.labels.keys(), registry=self.registry),
        )

    def metric__community_score(self) -> str:
        """ Metric representing the community score of this software

        Returns:
            str float representing the community score of this software
        """
        score = self.data['community_score']
        if score is None:
            return '0'
        return str(score)

    def metric__community_surveys(self) -> str:
        """ Metric representing this software's community survey count

        Returns:
            str integer representing the software's community survey count
        """
        return str(self.data['community_survey_count'])

    def metric__created(self) -> str:
        """ Metric representing the epoch time this software was created

        Returns:
            str integer representing the epoch time software was created
        """
        return str(dateparse(self.data['created']).strftime('%s'))

    def metric__downloads(self) -> str:
        """ Metric representing this software's download count

        Returns:
            str integer representing the software's download count
        """
        return str(self.data['download_count'])

    def metric__modified(self) -> str:
        """ Metric representing the epoch time this software was last modified

        Returns:
            str integer representing the epoch time software was last modified
        """
        return str(dateparse(self.data['modified']).strftime('%s'))

    async def update(self):
        """ Fetch and cache latest data from Galaxy

        Returns:
            str of json data from Galaxy
        """
        fastapi_logger.info('Fetching %s "%s" metadata',
                            self.__class__.__name__, self.name)
        # Ensure no two lookups occur at the same time
        async with asyncio.Lock():
            text = await fetch_from_url(self.url(), self.__class__.__name__,
                                        self.name)
            if text is None:
                return None
            jdata = json.loads(text)
        self.last_update = datetime.now()
        return jdata

    def needs_update(self, cache_seconds: int = CACHE_SECONDS) -> bool:
        """ Check if instance's data cache is out of date

        Args:
            cache_seconds: Maximum allowed age of data cache

        Returns:
            bool: Is cache sufficiently old that an update is required
        """
        if self.last_update is None:
            return True
        if (datetime.now() - self.last_update).seconds > cache_seconds:
            return True
        return False


class Collection(GalaxyData):
    """Ansible Galaxy Collection data

    Args:
        name (str): Full name of collection.

    Attributes:
        name (str): Full name of collection or role.
        labels (dict): Mappings of Prometheus label names to label values
        registry (prometheus_client.CollectorRegistry): Instance of Prometheus
            client 'CollectorRegistry' for storing metrics
        data (dict): Raw json data from Ansible Galaxy regarding collection or role
        metrics (dict): Maps str names of Prometheus metrics to Prometheus client
            metric instances
        last_update (datetime): Datetime of last time Galaxy data was fetched
    """
    def __init__(self, name: str) -> None:
        self.maintainer, self.collection = name.split('.', 2)
        self.labels = dict(category='collection', maintainer=self.maintainer,
                           project=self.collection)
        super().__init__(name)

    def metric__dependencies(self):
        """ Metric representing this collection's dependency count

        Returns:
            str integer of the collection's number of dependencies
        """
        return str(len(self.data['latest_version']['metadata']['dependencies']))

    def metric__quality_score(self):
        """ Metric representing this collection's quality score number

        Returns:
            str float of the collection's quality score number
        """
        score = self.data['latest_version']['quality_score']
        if score is None:
            return '0'
        return str(score)

    def url(self) -> str:
        """ URL of API data for this collection

        Returns:
            str URL for fetching API data
        """
        return 'https://galaxy.ansible.com/api/internal/ui/collections/' \
            f'{self.maintainer}/{self.collection}/?format=json'

    def metric__version(self):
        """ Metric representing this collection's current version

        Returns:
            str of the collection's current version
        """
        return self.data['latest_version']['version']

    def metric__versions(self) -> str:
        """ Metric representing this collection's total number of releases
        (versions)

        Returns:
            str integer representing the number of releases
        """
        return str(len(self.data['all_versions']))

    def _setup_metrics(self) -> dict:
        """ Configures Prometheus metrics for this collection.
        Metrics should only be setup when this class is initialized. Metrics
        are stored in the 'metrics' class attribute and can be updated over
        time

        Returns:
            Dict containing Prometheus metrics for this collection
        """
        metric_prefix = 'ansible_galaxy_collection_'
        metrics = self._setup_generic_metrics(metric_prefix)
        metrics.update(
            dict(
                dependency=Gauge(f'{metric_prefix}dependencies', 'Dependency count',
                                 self.labels.keys(), registry=self.registry),
            )
        )
        return metrics


class Role(GalaxyData):
    """Ansible Galaxy Role data

    Args:
        name (str): Full name role.

    Attributes:
        name (str): Full name of collection or role.
        labels (dict): Mappings of Prometheus label names to label values
        registry (prometheus_client.CollectorRegistry): Instance of Prometheus
            client 'CollectorRegistry' for storing metrics
        data (dict): Raw json data from Ansible Galaxy regarding collection or role
        metrics (dict): Maps str names of Prometheus metrics to Prometheus client
            metric instances
        last_update (datetime): Datetime of last time Galaxy data was fetched
    """
    def __init__(self, name: str) -> None:
        self.maintainer, self.role = name.split('.', 2)
        self.labels = dict(category='role', maintainer=self.maintainer,
                           project=self.role)
        super().__init__(name)

    def url(self) -> str:
        """ URL of API data for this role

        Returns:
            str URL for fetching API data
        """
        return 'https://galaxy.ansible.com/api/internal/ui/' \
            'repo-or-collection-detail/?format=json&namespace=' \
            f'{self.maintainer}&name={self.role}'

    def _setup_metrics(self) -> dict:
        """ Configures Prometheus metrics for this role.
        Metrics should only be setup when this class is initialized. Metrics
        are stored in the 'metrics' class attribute and can be updated over
        time

        Returns:
            Dict containing Prometheus metrics for this role
        """
        metric_prefix = 'ansible_galaxy_role_'
        metrics = self._setup_generic_metrics(metric_prefix)
        metrics.update(
            dict(
                fork=Gauge(f'{metric_prefix}forks', 'Fork count',
                           self.labels.keys(), registry=self.registry),
                imported=Gauge(f'{metric_prefix}imported',
                               'Imported datetime in epoch format',
                               self.labels.keys(), registry=self.registry),
                open_issue=Gauge(f'{metric_prefix}open_issues', 'Open Issues count',
                                 self.labels.keys(), registry=self.registry),
                star=Gauge(f'{metric_prefix}stars', 'Stars count',
                           self.labels.keys(), registry=self.registry),
                watchers=Gauge(f'{metric_prefix}watchers', 'Watcher count',
                               self.labels.keys(), registry=self.registry),
            )
        )
        return metrics

    def metric__quality_score(self) -> str:
        """ Metric representing the Ansible Galaxy quality score for this role

        Returns:
            str float representing the Ansible Galaxy score
        """
        score = self.data['quality_score']
        if score is None:
            return '0'
        return str(score)

    def metric__forks(self) -> str:
        """ Metric representing the total number of Github forks for this role

        Returns:
            str integer representing the total number of Github forks
        """
        return str(self.data['forks_count'])

    def metric__imported(self):
        """ Metric representing the epoch time this role was last imported into
        Ansible Galaxy

        Returns:
            str integer representing the epoch time of last Ansible Galaxy
            import
        """
        imported = dateparse(self.data['summary_fields']['latest_import']['finished'])
        return str(imported.strftime('%s'))

    def metric__open_issues(self) -> str:
        """ Metric representing the total number of Github open issues for this
        role

        Returns:
            str integer representing the total number of Github open issues
        """
        return str(self.data['open_issues_count'])

    def metric__stars(self) -> str:
        """ Metric representing the total number of Github stars for this role

        Returns:
            str integer representing the total number of Github stars
        """
        return str(self.data['stargazers_count'])

    def metric__watchers(self) -> str:
        """ Metric representing the total Ansible Galaxy watchers for this role

        Returns:
            str integer representing the total number Ansible Galaxy watchers
        """
        return str(self.data['watchers_count'])

    def metric__version(self):
        """ Metric representing this role's current version

        Returns:
            str of the role's current version
        """
        return self.data['summary_fields']['versions'][0]['version']

    def metric__versions(self):
        """ Metric representing this role's total number of releases (versions)

        Returns:
            str integer representing the number of releases
        """
        return str(len(self.data['summary_fields']['versions']))


async def fetch_from_url(url: str, job: str, instance: str, retries: int = 5) -> Optional[str]:
    """ Fetch content from specified URL
    URL will be retried up to 'retries' times

    Args:
        url: str URL to fetch
        job: Class name or other description of download type, used when
        logging
        instance: Specific software instance being downloaded, used when
        logging
        retries: int specifying the number of times to retry URL

    Returns:
        The supplied 'Collection' class instance
    """
    count = 0
    try:
        async for attempt in AsyncRetrying(stop=stop_after_delay(retries)):
            with attempt:
                count += 1
                if count > 1:
                    fastapi_logger.info('Fetching %s "%s" metadata (try %s)',
                                        job, instance, count)
                # Create HTTP session
                async with aiohttp.ClientSession() as session:
                    # Fetch latest JSON from Ansible Galaxy API
                    async with session.get(url) as response:
                        # Cache latest JSON
                        return await response.text()
    except RetryError:
        fastapi_logger.exception('Error fetching %s "%s" URL %s', job,
                                 instance, url)
    return None


def set_collection_metrics(collection: Collection) -> Collection:
    """ Set Prometheus metrics on the supplied 'Collection' instance based on
    metrics defined within the 'Collection' instance

    Args:
        collection: 'Collection' class instance

    Returns:
        The supplied 'Collection' class instance
    """
    collection.metrics['community_score'].labels(**collection.labels)\
        .set(collection.metric__community_score())
    collection.metrics['community_survey'].labels(**collection.labels)\
        .set(collection.metric__community_surveys())
    collection.metrics['created'].labels(**collection.labels).set(collection.metric__created())
    collection.metrics['dependency'].labels(**collection.labels)\
        .set(collection.metric__dependencies())
    collection.metrics['download'].labels(**collection.labels).set(collection.metric__downloads())
    collection.metrics['modified'].labels(**collection.labels).set(collection.metric__modified())
    collection.metrics['quality_score'].labels(**collection.labels)\
        .set(collection.metric__quality_score())
    collection.metrics['version'].labels(**collection.labels)\
        .info({'version': collection.metric__version()})
    collection.metrics['versions'].labels(**collection.labels).set(collection.metric__versions())
    return collection


def set_role_metrics(role: Role) -> Role:
    """ Set Prometheus metrics on the supplied 'Role' instance based on metrics
    defined within the 'Role' instance

    Args:
        role: 'Role' class instance

    Returns:
        The supplied 'Role' class instance
    """
    role.metrics['community_score'].labels(**role.labels).set(role.metric__community_score())
    role.metrics['community_survey'].labels(**role.labels).set(role.metric__community_surveys())
    role.metrics['created'].labels(**role.labels).set(role.metric__created())
    role.metrics['download'].labels(**role.labels).set(role.metric__downloads())
    role.metrics['fork'].labels(**role.labels).set(role.metric__forks())
    role.metrics['imported'].labels(**role.labels).set(role.metric__imported())
    role.metrics['modified'].labels(**role.labels).set(role.metric__modified())
    role.metrics['open_issue'].labels(**role.labels).set(role.metric__open_issues())
    role.metrics['quality_score'].labels(**role.labels).set(role.metric__quality_score())
    role.metrics['star'].labels(**role.labels).set(role.metric__stars())
    role.metrics['version'].labels(**role.labels).info({'version': role.metric__version()})
    role.metrics['versions'].labels(**role.labels).set(role.metric__versions())
    role.metrics['watchers'].labels(**role.labels).set(role.metric__watchers())
    return role


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    """ Generate root HTML page

    Returns:
        str HTML base index page
    """
    return ROOT_HTML


@app.get("/metrics", response_class=PlainTextResponse)
async def process_metrics() -> str:
    """ Fetch this exporter's own Prometheus metrics

    Returns:
        str in Prometheus' exporter format of this exporters metrics
    """
    update_base_metrics()
    return generate_latest()


@app.get('/collection/{collection_name}', response_class=HTMLResponse)
async def collection_base(collection_name: str) -> str:
    """ Generate collection base HTML page

    Args:
        collection_name: The name of a collection

    Returns:
        str HTML of an index page listing URLs available for collection metrics
    """
    return COLLECTION_HTML.format(collection_name=collection_name)


@app.get('/probe', response_class=PlainTextResponse)
async def probe(module: str, target: str) -> str:
    """ Generate collection or role's Prometheus metrics
    URLs must be in the Prometheus "Multi Target Exporter" format, example:
    /probe?module=role&target=mesaguy.prometheus

    Args:
        module: One of 'collection' or 'role'
        target: The name of the collection or role, ie: 'mesaguy.prometheus'

    Returns:
        str in Prometheus' exporter format of specified collection or
        role's metrics
    """
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
async def collection_metric(collection_name: str, metric: str) -> str:
    """ Generate collection's Prometheus metrics

    Args:
        collection_name: The name of a collection
        metric: The name of a specific metric or 'metrics' for all Prometheus
        metrics

    Returns:
        str in Prometheus' exporter format of specified collection's metrics
    """
    collection = await get_collection(collection_name)
    if metric == 'metrics':
        collection = set_collection_metrics(collection)
        return generate_latest(registry=collection.registry)
    return getattr(collection, f'metric__{metric}')()


@app.get('/role/{role_name}', response_class=HTMLResponse)
async def role_base(role_name: str) -> str:
    """ Generate role base HTML page

    Args:
        role_name: The name of a role

    Returns:
        str HTML of an index page listing URLs available for role metrics
    """
    return ROLE_HTML.format(role_name=role_name)


@app.get('/role/{role_name}/{metric}', response_class=PlainTextResponse)
async def role_metric(role_name: str, metric: str) -> str:
    """ Generate role's Prometheus metrics

    Args:
        role_name: The name of a role
        metric: The name of a specific metric or 'metrics' for all Prometheus
        metrics

    Returns:
        str in Prometheus' exporter format of specified role's metrics
    """
    role = await get_role(role_name)
    if metric == 'metrics':
        role = set_role_metrics(role)
        return generate_latest(registry=role.registry)
    return getattr(role, f'metric__{metric}')()


def update_base_metrics(increment: bool = False) -> dict:
    """ Update this exporter's own Prometheus metrics

    Args:
        increment: Increment the count of total Ansible Galaxy API calls by one

    Returns:
        Dict containing base metrics
    """
    if 'version' not in METRICS:
        METRICS['version'] = Info('ansible_galaxy_exporter_version',
                                  'Current exporter version')
        METRICS['version'].info({'version': __version__})
    if 'api_call_count' not in METRICS:
        METRICS['api_call_count'] = Counter('ansible_galaxy_exporter_api_call_count',
                                            'API calls to Ansible Galaxy')
    if increment:
        METRICS['api_call_count'].inc()
    return METRICS


async def get_collection(collection_name: str) -> Collection:
    """ Fetch collection information and populate a Collection instance

    Args:
        collection_name: The name of a collection, in author.project format

    Returns:
        A 'Collection' class instance
    """
    update_base_metrics(increment=True)
    if collection_name not in COLLECTIONS:
        COLLECTIONS[collection_name] = Collection(collection_name)
    collection = COLLECTIONS[collection_name]
    if collection.needs_update():
        data = await collection.update()
        collection.data = data
    return collection


async def get_role(role_name: str) -> Role:
    """ Fetch role information and populate a Role instance

    Args:
        role_name: The name of a role, in author.project format

    Returns:
        A 'Role' class instance
    """
    update_base_metrics(increment=True)
    if role_name not in ROLES:
        ROLES[role_name] = Role(role_name)
    role = ROLES[role_name]
    if role.needs_update():
        data = await role.update()
        role.data = data['data']['repository']
    return role
