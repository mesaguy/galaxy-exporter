# Alpine based Ansible Galaxy Role statistics collector

[![DockerHub Badge](http://dockeri.co/image/mesaguy/ansible_galaxy_role_stats)](https://hub.docker.com/r/mesaguy/ansible_galaxy_role_stats)

## Introduction

This container image collects Ansible Galaxy statistics for a role and makes the statistics available via HTTP for Prometheus and very simple collectors.

Runs on port 8000/tcp as the user 'nobody' and daemon logs are send to stdout.

## Usage

The most basic usage is the following, which monitors the [mesaguy.prometheus](https://github.com/mesaguy/ansible-prometheus) role's statistics:

    docker run --rm -p 8000:8000 -it mesaguy/ansible_galaxy_role_stats

To monitor a different role, first identify the role's Ansible Galaxy role ID number. For example, the *mesaguy.prometheus* role ID is *29232*:

    ansible-galaxy info mesaguy.prometheus

Or

    ansible-galaxy info dev-sec.ssh-hardening

Example that monitors the *dev-sec.ssh-hardening* role metrics:

    docker run -it -e ANSIBLE_ROLE_ID=10533 -e ANSIBLE_ROLE_NAME=dev-sec.ssh-hardening -p 8000:8000 mesaguy/ansible_galaxy_role_stats

By default, all Ansible Galaxy results are cached for 5 minutes to ensure Ansible Galaxy isn't polled excessively. This value can be changed with the ```CACHE_SECONDS``` environmental variable.

## Metrics

A ```curl localhost:8000``` returns:

    <html>
        <head>
            <title>dev-sec.ssh-hardening Index</title>
        </head>
        <body>
            <p>
                <a href="/metrics">Prometheus Metrics</a>
            </p>
            <p>
                Simple metrics for dev-sec.ssh-hardening
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

Prometheus formatted metrics are located at ```/metrics``` and all other metrics are available on their own URL

For instance to gather just the star count, ```curl localhost:8000/stars``` returns ```663```. Note that the result has no trailing newline. These simple metrics are useful for polling from simple devices like Arduinos.

### Prometheus

All Ansible Galaxy metrics are prefixed with ```ansible_galaxy_role```, then have the role's name with all ```.``` and ```-``` characters converted to underscores, then the type of collected data is specified (ie: _stars).

Example Prometheus metrics from running ```curl localhost:8000/metrics```:

    # HELP python_gc_objects_collected_total Objects collected during gc
    # TYPE python_gc_objects_collected_total counter
    python_gc_objects_collected_total{generation="0"} 6212.0
    python_gc_objects_collected_total{generation="1"} 321.0
    python_gc_objects_collected_total{generation="2"} 0.0
    # HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
    # TYPE python_gc_objects_uncollectable_total counter
    python_gc_objects_uncollectable_total{generation="0"} 0.0
    python_gc_objects_uncollectable_total{generation="1"} 0.0
    python_gc_objects_uncollectable_total{generation="2"} 0.0
    # HELP python_gc_collections_total Number of times this generation was collected
    # TYPE python_gc_collections_total counter
    python_gc_collections_total{generation="0"} 99.0
    python_gc_collections_total{generation="1"} 8.0
    python_gc_collections_total{generation="2"} 0.0
    # HELP python_info Python platform information
    # TYPE python_info gauge
    python_info{implementation="CPython",major="3",minor="8",patchlevel="3",version="3.8.3"} 1.0
    # HELP process_virtual_memory_bytes Virtual memory size in bytes.
    # TYPE process_virtual_memory_bytes gauge
    process_virtual_memory_bytes 7.2306688e+07
    # HELP process_resident_memory_bytes Resident memory size in bytes.
    # TYPE process_resident_memory_bytes gauge
    process_resident_memory_bytes 3.6446208e+07
    # HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
    # TYPE process_start_time_seconds gauge
    process_start_time_seconds 1.59286511727e+09
    # HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
    # TYPE process_cpu_seconds_total counter
    process_cpu_seconds_total 1.2
    # HELP process_open_fds Number of open file descriptors.
    # TYPE process_open_fds gauge
    process_open_fds 16.0
    # HELP process_max_fds Maximum number of open file descriptors.
    # TYPE process_max_fds gauge
    process_max_fds 1.048576e+06
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_created Created datetime in epoch format
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_created gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_created{ansible_role_id="10533",ansible_role_name="dev-sec.ssh-hardening"} 1.466782044e+09
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_downloads Download count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_downloads gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_downloads{ansible_role_id="10533",ansible_role_name="dev-sec.ssh-hardening"} 378666.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_forks Fork count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_forks gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_forks{ansible_role_id="10533",ansible_role_name="dev-sec.ssh-hardening"} 190.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_modified Modified datetime in epoch format
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_modified gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_modified{ansible_role_id="10533",ansible_role_name="dev-sec.ssh-hardening"} 1.592851307e+09
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_open_issues Open Issues count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_open_issues gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_open_issues{ansible_role_id="10533",ansible_role_name="dev-sec.ssh-hardening"} 10.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_stars Stars count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_stars gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_stars{ansible_role_id="10533",ansible_role_name="dev-sec.ssh-hardening"} 663.0
    # HELP ansible_galaxy_role_dev_sec_ssh_hardening_versions Version count
    # TYPE ansible_galaxy_role_dev_sec_ssh_hardening_versions gauge
    ansible_galaxy_role_dev_sec_ssh_hardening_versions{ansible_role_id="10533",ansible_role_name="dev-sec.ssh-hardening"} 31.0
