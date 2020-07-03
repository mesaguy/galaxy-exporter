# Prometheus exporter of Ansible Galaxy metrics

[![DockerHub Badge](http://dockeri.co/image/mesaguy/galaxy-exporter)](https://hub.docker.com/r/mesaguy/galaxy-exporter)

## Introduction

This container image collects Ansible Galaxy metrics and makes the metrics available via HTTP for Prometheus and very simple collectors.

Runs on port 9288/tcp as the user 'nobody' and daemon logs are send to stdout.

## Usage

### Basic install

Clone the python code:

    git clone https://github.com/mesaguy/galaxy-exporter.git

Install:

    cd galaxy_exporter
    ./setup.py install

The application can be run locally via:

    uvicorn galaxy_exporter.galaxy_exporter:app --port 9288 --reload

### Docker

The most basic usage is the following, which starts the exporter:

    docker run --rm -p 9288:9288 -it mesaguy/galaxy-exporter

By default, all Ansible Galaxy results are cached for 15 seconds to ensure Ansible Galaxy isn't polled excessively. This value can be changed with the ```CACHE_SECONDS``` environmental variable. Setting the cache value to ```0``` disables caching completely.

### Kubernetes

The following will can be used to get started. No roles or collections need to be specified:

    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: galaxy-exporter
      labels:
        app: galaxy-exporter
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: galaxy-exporter
      template:
        metadata:
          labels:
            app: galaxy-exporter
        spec:
          containers:
          - name: galaxy-exporter
            image: mesaguy/galaxy-exporter:latest
            env:
             - name: CACHE_SECONDS
               value: '600'
            ports:
            - containerPort: 9288
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: galaxy-exporter
    spec:
      ports:
      - name: http
        port: 9288
        protocol: TCP
        targetPort: 9288
      selector:
        app: galaxy-exporter
      type: LoadBalancer

### Prometheus server configuration

Make a Ansible Galaxy exporter configuration directory:

    mkdir -p /etc/prometheus/galaxy

The Ansible Galaxy exporter uses [Multi Target Exporter](https://prometheus.io/docs/guides/multi-target-exporter/) style polling similar to the blackbox-exporter. Multiple roles and collections can be specified as follows:

> /etc/prometheus/galaxy/collections.yml

    ---
    - targets:
      - community.kubernetes
      - netbox.netbox

> /etc/prometheus/galaxy/roles.yml

    ---
    - targets:
      - mesaguy.prometheus
      - dev-sec.ssh-hardening

Add a configuration like the following to your Prometheus configuration file. Replace **ansible-galaxy-host** with your applicable hostname:

    # Ansible Galaxy Exporter
    - job_name: galaxy
      static_configs:
      - targets:
        - ansible-galaxy-host:9288

    # Ansible Galaxy Exporter - Collections
    - job_name: galaxy.collection
      file_sd_configs:
      - files:
        - /etc/prometheus/galaxy/collections.yml
      metrics_path: /probe
      params:
        module:
        - collection
      relabel_configs:
      - source_labels:
        - __address__
        target_label: __param_target
      - source_labels:
        - __param_target
        target_label: instance
      - replacement: ansible-galaxy-host:9288
        target_label: __address__
      scrape_interval: 60s

    # Ansible Galaxy Exporter - Roles
    - job_name: galaxy.role
      file_sd_configs:
      - files:
        - /etc/prometheus/galaxy/roles.yml
      metrics_path: /probe
      params:
        module:
        - role
      relabel_configs:
      - source_labels:
        - __address__
        target_label: __param_target
      - source_labels:
        - __param_target
        target_label: instance
      - replacement: ansible-galaxy-host:9288
        target_label: __address__
      scrape_interval: 60s

## Ansible role metrics

A ```curl localhost:9288/role/dev-sec.ssh-hardening``` returns:

    <html>
        <head>
            <title>Ansible Galaxy role dev-sec.ssh-hardening statistics index</title>
        </head>
        <body>
            <p>
                <a href="/role/dev-sec.ssh-hardening/metrics">Prometheus Metrics for dev-sec.ssh-hardening</a>
            </p>
            <p>
                Simple metrics for dev-sec.ssh-hardening
                <ul>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/community_score">Community score </a> count integer</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/community_surveys">Community surveys</a> count integer</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/created">Created </a> epoch format datetime</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/dependencies">Dependencies </a> count integer</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/downloads">Download </a> count integer</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/forks">Forks </a> count integer</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/imported">Imported </a> epoch format datetime</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/modified">Modified </a> epoch format datetime</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/open_issues">Open Issues </a> count integer</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/platforms">Platforms </a> count integer</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/quality_score">Quality score </a> count integer</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/stars">Star </a> count integer</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/version">Version </a> current version</li>
                    <li>Raw <a href="/role/dev-sec.ssh-hardening/versions">Versions </a> count integer</li>
                </ul>
            </p>
        </body>
    </html>

To gather just the star count, ```curl localhost:9288/role/dev-sec.ssh-hardening/stars``` returns ```663```. Note that the result has no trailing newline. These simple metrics are useful for polling from simple devices like Arduinos.

### Prometheus role metrics

All Ansible Galaxy metrics are prefixed with ```ansible_galaxy_role```, then have the role's name with all ```.``` and ```-``` characters converted to underscores, then the type of collected data is specified (ie: _stars).

Example Prometheus role metrics from running ```curl localhost:9288/role/dev-sec.ssh-hardening/metrics```:

    # HELP ansible_galaxy_role_created Created datetime in epoch format
    # TYPE ansible_galaxy_role_created gauge
    ansible_galaxy_role_created{category="role",maintainer="dev-sec",unit="ssh-hardening"} 1.46392447e+09
    # HELP ansible_galaxy_role_community_score Community score
    # TYPE ansible_galaxy_role_community_score gauge
    ansible_galaxy_role_community_score{category="role",maintainer="dev-sec",unit="ssh-hardening"} 5.0
    # HELP ansible_galaxy_role_community_surveys Community surveys
    # TYPE ansible_galaxy_role_community_surveys gauge
    ansible_galaxy_role_community_surveys{category="role",maintainer="dev-sec",unit="ssh-hardening"} 1.0
    # HELP ansible_galaxy_role_downloads Download count
    # TYPE ansible_galaxy_role_downloads gauge
    ansible_galaxy_role_downloads{category="role",maintainer="dev-sec",unit="ssh-hardening"} 389480.0
    # HELP ansible_galaxy_role_modified Modified datetime in epoch format
    # TYPE ansible_galaxy_role_modified gauge
    ansible_galaxy_role_modified{category="role",maintainer="dev-sec",unit="ssh-hardening"} 1.593743716e+09
    # HELP ansible_galaxy_role_quality_score Quality score
    # TYPE ansible_galaxy_role_quality_score gauge
    ansible_galaxy_role_quality_score{category="role",maintainer="dev-sec",unit="ssh-hardening"} 4.75
    # HELP ansible_galaxy_role_version_info Current release version
    # TYPE ansible_galaxy_role_version_info gauge
    ansible_galaxy_role_version_info{category="role",maintainer="dev-sec",unit="ssh-hardening",version="9.2.0"} 1.0
    # HELP ansible_galaxy_role_versions Version count
    # TYPE ansible_galaxy_role_versions gauge
    ansible_galaxy_role_versions{category="role",maintainer="dev-sec",unit="ssh-hardening"} 31.0
    # HELP ansible_galaxy_role_forks Fork count
    # TYPE ansible_galaxy_role_forks gauge
    ansible_galaxy_role_forks{category="role",maintainer="dev-sec",unit="ssh-hardening"} 190.0
    # HELP ansible_galaxy_role_imported Imported datetime in epoch format
    # TYPE ansible_galaxy_role_imported gauge
    ansible_galaxy_role_imported{category="role",maintainer="dev-sec",unit="ssh-hardening"} 1.593555814e+09
    # HELP ansible_galaxy_role_open_issues Open Issues count
    # TYPE ansible_galaxy_role_open_issues gauge
    ansible_galaxy_role_open_issues{category="role",maintainer="dev-sec",unit="ssh-hardening"} 10.0
    # HELP ansible_galaxy_role_stars Stars count
    # TYPE ansible_galaxy_role_stars gauge
    ansible_galaxy_role_stars{category="role",maintainer="dev-sec",unit="ssh-hardening"} 668.0
    # HELP ansible_galaxy_role_watchers Watcher count
    # TYPE ansible_galaxy_role_watchers gauge
    ansible_galaxy_role_watchers{category="role",maintainer="dev-sec",unit="ssh-hardening"} 56.0

## Ansible collection metrics

A ```curl localhost:9288/collection/community.kubernetes``` returns:

    <html>
        <head>
            <title>Ansible Galaxy collection community.kubernetes statistics index</title>
        </head>
        <body>
            <p>
                <a href="/collection/community.kubernetes/metrics">Prometheus Metrics for community.kubernetes</a>
            </p>
            <p>
                Simple metrics for community.kubernetes
                <ul>
                    <li>Raw <a href="/collection/community.kubernetes/community_score">Community score </a> count integer</li>
                    <li>Raw <a href="/collection/community.kubernetes/community_surveys">Community surveys</a> count integer</li>
                    <li>Raw <a href="/collection/community.kubernetes/created">Created </a> epoch format datetime</li>
                    <li>Raw <a href="/collection/community.kubernetes/dependencies">Dependencies </a> count integer</li>
                    <li>Raw <a href="/collection/community.kubernetes/downloads">Download </a> count integer</li>
                    <li>Raw <a href="/collection/community.kubernetes/modified">Modified </a> epoch format datetime</li>
                    <li>Raw <a href="/collection/community.kubernetes/quality_score">Quality score </a> count integer</li>
                    <li>Raw <a href="/collection/community.kubernetes/version">Version </a> current version</li>
                    <li>Raw <a href="/collection/community.kubernetes/versions">Versions </a> count integer</li>
                </ul>
            </p>
        </body>
    </html>

### Prometheus collection metrics

All Ansible Galaxy collection metrics are prefixed with ```ansible_galaxy_collection```, then have the collection's name with all ```.``` and ```-``` characters converted to underscores, then the type of collected data is specified (ie: _downloads).

Example Prometheus metrics from running ```localhost:9288/collection/community.kubernetes/metrics```:

    # HELP ansible_galaxy_collection_created Created datetime in epoch format
    # TYPE ansible_galaxy_collection_created gauge
    ansible_galaxy_collection_created{category="collection",maintainer="community",unit="kubernetes"} 1.58089728e+09
    # HELP ansible_galaxy_collection_community_score Community score
    # TYPE ansible_galaxy_collection_community_score gauge
    ansible_galaxy_collection_community_score{category="collection",maintainer="community",unit="kubernetes"} 0.0
    # HELP ansible_galaxy_collection_community_surveys Community surveys
    # TYPE ansible_galaxy_collection_community_surveys gauge
    ansible_galaxy_collection_community_surveys{category="collection",maintainer="community",unit="kubernetes"} 0.0
    # HELP ansible_galaxy_collection_downloads Download count
    # TYPE ansible_galaxy_collection_downloads gauge
    ansible_galaxy_collection_downloads{category="collection",maintainer="community",unit="kubernetes"} 360534.0
    # HELP ansible_galaxy_collection_modified Modified datetime in epoch format
    # TYPE ansible_galaxy_collection_modified gauge
    ansible_galaxy_collection_modified{category="collection",maintainer="community",unit="kubernetes"} 1.593619976e+09
    # HELP ansible_galaxy_collection_quality_score Quality score
    # TYPE ansible_galaxy_collection_quality_score gauge
    ansible_galaxy_collection_quality_score{category="collection",maintainer="community",unit="kubernetes"} 0.0
    # HELP ansible_galaxy_collection_version_info Current release version
    # TYPE ansible_galaxy_collection_version_info gauge
    ansible_galaxy_collection_version_info{category="collection",maintainer="community",unit="kubernetes",version="0.11.1"} 1.0
    # HELP ansible_galaxy_collection_versions Version count
    # TYPE ansible_galaxy_collection_versions gauge
    ansible_galaxy_collection_versions{category="collection",maintainer="community",unit="kubernetes"} 4.0
    # HELP ansible_galaxy_collection_dependencies Dependency count
    # TYPE ansible_galaxy_collection_dependencies gauge
    ansible_galaxy_collection_dependencies{category="collection",maintainer="community",unit="kubernetes"} 0.0

## License
MIT
See the [LICENSE](https://github.com/mesaguy/galaxy-exporter/blob/master/LICENSE) file

## Author Information
Mesaguy
 - https://mesaguy.com
 - https://github.com/mesaguy/galaxy-exporter
