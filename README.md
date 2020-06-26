# Alpine based Prometheus exporter of Ansible Galaxy metrics

[![DockerHub Badge](http://dockeri.co/image/mesaguy/galaxy-exporter)](https://hub.docker.com/r/mesaguy/galaxy-exporter)

## Introduction

This container image collects Ansible Galaxy metrics and makes the metrics available via HTTP for Prometheus and very simple collectors.

Runs on port 8000/tcp as the user 'nobody' and daemon logs are send to stdout.

## Usage

### Basic install

Clone the python code:

    git clone https://github.com/mesaguy/galaxy_exporter.git

Install:

    cd galaxy_exporter
    ./setup.py install

The application can be run locally via:

    uvicorn galaxy_exporter.galaxy_exporter:app --reload

### Docker

The most basic usage is the following, which starts the exporter:

    docker run --rm -p 8000:8000 -it mesaguy/galaxy-exporter

By default, all Ansible Galaxy results are cached for 15 seconds to ensure Ansible Galaxy isn't polled excessively. This value can be changed with the ```CACHE_SECONDS``` environmental variable. Setting the cache value to ```0``` disables caching completely.

## Ansible role metrics

A ```curl localhost:8000/role/dev-sec.ssh-hardening``` returns:

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

To gather just the star count, ```curl localhost:8000/role/dev-sec.ssh-hardening/stars``` returns ```663```. Note that the result has no trailing newline. These simple metrics are useful for polling from simple devices like Arduinos.

### Prometheus role metrics

All Ansible Galaxy metrics are prefixed with ```ansible_galaxy_role```, then have the role's name with all ```.``` and ```-``` characters converted to underscores, then the type of collected data is specified (ie: _stars).

Example Prometheus role metrics from running ```curl localhost:8000/role/dev-sec.ssh-hardening/metrics```:

    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_created Created datetime in epoch format
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_created gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_created{role_name="dev-sec.ssh-hardening"} 1.466782044e+09
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_community_score Community score
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_community_score gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_community_score{role_name="dev-sec.ssh-hardening"} 5.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_community_surveys Community surveys
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_community_surveys gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_community_surveys{role_name="dev-sec.ssh-hardening"} 1.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_dependencies Dependency count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_dependencies gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_dependencies{role_name="dev-sec.ssh-hardening"} 0.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_downloads Download count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_downloads gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_downloads{role_name="dev-sec.ssh-hardening"} 382509.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_modified Modified datetime in epoch format
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_modified gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_modified{role_name="dev-sec.ssh-hardening"} 1.593090008e+09
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_quality_score Quality score
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_quality_score gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_quality_score{role_name="dev-sec.ssh-hardening"} 4.75
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_version_info Current release version
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_version_info gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_version_info{version="9.2.0"} 1.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_versions Version count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_versions gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_versions{role_name="dev-sec.ssh-hardening"} 32.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_forks Fork count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_forks gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_forks{role_name="dev-sec.ssh-hardening"} 190.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_imported Imported datetime in epoch format
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_imported gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_imported{role_name="dev-sec.ssh-hardening"} 1.593075608e+09
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_platforms Platform count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_platforms gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_platforms{role_name="dev-sec.ssh-hardening"} 38.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_open_issues Open Issues count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_open_issues gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_open_issues{role_name="dev-sec.ssh-hardening"} 9.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_stars Stars count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_stars gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_stars{role_name="dev-sec.ssh-hardening"} 665.0

## Ansible collection metrics

A ```curl localhost:8000/collection/community.kubernetes``` returns:

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

Example Prometheus metrics from running ```localhost:8000/collection/community.kubernetes/metrics```:

    # HELP ansible_galaxy_collection_community_kubernetes_created Created datetime in epoch format
    # TYPE ansible_galaxy_collection_community_kubernetes_created gauge
    ansible_galaxy_collection_community_kubernetes_created{collection_name="community.kubernetes"} 1.58089728e+09
    # HELP ansible_galaxy_collection_community_kubernetes_community_score Community score
    # TYPE ansible_galaxy_collection_community_kubernetes_community_score gauge
    ansible_galaxy_collection_community_kubernetes_community_score{collection_name="community.kubernetes"} 0.0
    # HELP ansible_galaxy_collection_community_kubernetes_community_surveys Community surveys
    # TYPE ansible_galaxy_collection_community_kubernetes_community_surveys gauge
    ansible_galaxy_collection_community_kubernetes_community_surveys{collection_name="community.kubernetes"} 0.0
    # HELP ansible_galaxy_collection_community_kubernetes_dependencies Dependency count
    # TYPE ansible_galaxy_collection_community_kubernetes_dependencies gauge
    ansible_galaxy_collection_community_kubernetes_dependencies{collection_name="community.kubernetes"} 0.0
    # HELP ansible_galaxy_collection_community_kubernetes_downloads Download count
    # TYPE ansible_galaxy_collection_community_kubernetes_downloads gauge
    ansible_galaxy_collection_community_kubernetes_downloads{collection_name="community.kubernetes"} 324060.0
    # HELP ansible_galaxy_collection_community_kubernetes_modified Modified datetime in epoch format
    # TYPE ansible_galaxy_collection_community_kubernetes_modified gauge
    ansible_galaxy_collection_community_kubernetes_modified{collection_name="community.kubernetes"} 1.588597767e+09
    # HELP ansible_galaxy_collection_community_kubernetes_quality_score Quality score
    # TYPE ansible_galaxy_collection_community_kubernetes_quality_score gauge
    ansible_galaxy_collection_community_kubernetes_quality_score{collection_name="community.kubernetes"} 0.0
    # HELP ansible_galaxy_collection_community_kubernetes_version_info Current release version
    # TYPE ansible_galaxy_collection_community_kubernetes_version_info gauge
    ansible_galaxy_collection_community_kubernetes_version_info{version="0.11.0"} 1.0
    # HELP ansible_galaxy_collection_community_kubernetes_versions Version count
    # TYPE ansible_galaxy_collection_community_kubernetes_versions gauge
    ansible_galaxy_collection_community_kubernetes_versions{collection_name="community.kubernetes"} 3.0

## License
MIT
See the [LICENSE](https://github.com/mesaguy/galaxy-exporter/blob/master/LICENSE) file

## Author Information
Mesaguy
 - https://mesaguy.com
 - https://github.com/mesaguy/galaxy-exporter
