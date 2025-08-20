from django.shortcuts import render, redirect
from . import forms

# Create your views here.

import requests
import os
from django.conf import settings
import json

from .models import Server

api_url_template = "https://{}:8008/{}"

# Construct the path to your CA file
# ca_file_path = os.path.join(settings.BASE_DIR, 'certs', 'cacert.pem')
ca_file_path = '/Users/marcusmao/Dev/Test/ca.pem'


class HistoryUnity:
    def __init__(self, tl, lsn, reason):
        self.tl = tl
        self.lsn = lsn
        self.reason = reason
        self.timestamp = ""
        self.new_leader = ""


class MemberUnity:
    def __init__(self, scope, name, role, state, api_url, host, port, timeline, lag, tags):
        self.scope = scope
        self.name = name
        self.role = role
        self.state = state
        self.api_url = api_url
        self.host = host
        self.port = port
        self.timeline = timeline
        self.lag = lag
        self.tags = tags


class ConfigUnity:
    def __init__(self, check_timeline, loop_wait, maximum_lag_on_failover, retry_timeout, ttl, postgresql_parameters,
                 postgresql_pg_hba):
        self.check_timeline = check_timeline
        self.loop_wait = loop_wait
        self.maximum_lag_on_failover = maximum_lag_on_failover
        self.retry_timeout = retry_timeout
        self.ttl = ttl
        self.postgresql_parameters = postgresql_parameters
        self.postgresql_pg_hba = postgresql_pg_hba


def fetch_data_from_api(ip, endpoint):
    api_url = api_url_template.format(ip, endpoint)

    try:
        # Make the GET request, specifying the CA certificate for verification
        response = requests.get(api_url, verify=ca_file_path)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Process the JSON response
        data = response.json()
        # data = json.dumps(data, indent=4)
        return data

    except requests.exceptions.RequestException as e:
        # Handle request-related errors (e.g., network issues, SSL errors)
        print(f"Error fetching data: {e}")
        return None
    except ValueError as e:
        # Handle JSON decoding errors
        print(f"Error decoding JSON: {e}")
        return None


def post_data_to_api(ip, endpoint, data):
    api_url = api_url_template.format(ip, endpoint)
    response = requests.post(api_url, json=data, verify=ca_file_path)

    if response.status_code == 200:  # 200 Created is common for successful POST
        print("Resource created successfully!")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False


def server(request):
    endpoint = "server"

    op = request.GET.get('op')
    host_ip = request.GET.get("host_ip")
    username = request.GET.get("username")
    print("host_ip", host_ip)
    if op == "edit":
        server = Server.objects.get(host_ip=host_ip, username=username)
    else:
        server = Server

    servers = Server.objects.all()
    for s in servers:
        print("Server: ", s.host_ip)
    print("Server list: ", servers)

    # form = forms.ServerForm()

    return render(request, 'patroni/server.html',
                  {'data': None, "endpoint": endpoint, "servers": servers, "server": server})


def add_server(request):
    endpoint = "server"
    if request.method == "POST":
        form = forms.ServerForm(request.POST)
        if form.is_valid():
            form.save()

    return redirect("patroni:server")  # render(request, "patroni/server.html")


def delete_server(request):
    endpoint = "server"
    host_ip = request.GET.get("host_ip")
    username = request.GET.get("username")
    print("Username: ", username)
    print("Host: ", host_ip)
    Server.objects.filter(host_ip=host_ip, username=username).delete()
    return redirect("patroni:server")


def patroni(request):
    # patroni, cluster, history, config
    # endpoint = request.GET.get("endpoint")
    # if endpoint is None:
    endpoint = "patroni"
    active = "active"
    json_data_array = []

    servers = Server.objects.values("host_ip").distinct()
    for s in servers:
    # for k, v in servers.items():
        print("Server: ", s["host_ip"])

        pretty_json_data = fetch_data_from_api(s["host_ip"], endpoint)
        pretty_json_data = json.dumps(pretty_json_data, indent=4)
        data = {"host_ip": s["host_ip"], "active": active, "json_data": pretty_json_data}
        active = ""
        json_data_array.append(data)
        print(pretty_json_data)

    return render(request, 'patroni/patroni.html',
                  {'data': json_data_array, "endpoint": endpoint})


def switchover(request):
    endpoint = "switchover"

    leader = request.GET.get("leader")
    candidate = request.GET.get("candidate")
    host_ip = request.GET.get("host_ip")
    p = {"leader": leader, "candidate": candidate}

    status = post_data_to_api(host_ip, "switchover", p)
    print(status)

    return redirect("patroni:cluster")


def restart(request):
    endpoint = "restart"

    host_ip = request.GET.get("host_ip")
    status = post_data_to_api(host_ip, "restart", None)

    return redirect("patroni:cluster")


def cluster(request):
    # patroni, cluster, history, config
    endpoint = "cluster"
    member_array = []

    server = Server.objects.all().first()

    data = fetch_data_from_api(server.host_ip, endpoint)
    pretty_json_data = json.dumps(data, indent=4)
    print(pretty_json_data)

    scope = data["scope"]
    print(data["scope"])
    for m in data["members"]:
        if m["role"] == "leader":
            leader = m["name"]

        member_obj = MemberUnity(scope, m["name"], m["role"], m["state"], m["api_url"], m["host"],
                                 m["port"],
                                 m.get("timeline"), m.get("lag"), m["tags"])
        member_array.append(member_obj)

    if data:
        return render(request, 'patroni/cluster.html',
                      {'data': member_array, "endpoint": endpoint, "leader": leader})
    else:
        return render(request, 'patroni/cluster.html',
                      {'message': 'Failed to fetch data', "endpoint": endpoint})


def history(request):
    # patroni, cluster, history, config
    endpoint = "history"
    history_array = []

    server = Server.objects.all().first()
    data = fetch_data_from_api(server.host_ip, endpoint)
    for r in data:
        history_obj = HistoryUnity(r[0], r[1], r[2])
        # print("Row length:", len(r))
        if len(r) > 3:
            history_obj.timestamp = r[3]
            history_obj.new_leader = r[4]
        history_array.append(history_obj)

    # print(data)
    if data:
        return render(request, 'patroni/history.html',
                      {'data': history_array, "endpoint": endpoint})
    else:
        return render(request, 'patroni/history.html',
                      {'message': 'Failed to fetch data', "endpoint": endpoint})


def config(request):
    # patroni, cluster, history, config
    endpoint = "config"
    server = Server.objects.all().first()
    pretty_json_data = fetch_data_from_api(server.host_ip, endpoint)
    pretty_json_data = json.dumps(pretty_json_data, indent=4)
    print(pretty_json_data)
    if pretty_json_data:
        return render(request, 'patroni/config.html',
                      {'data': pretty_json_data, "endpoint": endpoint})
    else:
        return render(request, 'patroni/config.html',
                      {'message': 'Failed to fetch data', "endpoint": endpoint})
