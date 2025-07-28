from django.shortcuts import render

# Create your views here.

import requests
import os
from django.conf import settings
import json

endpoints = {"patroni": "/patroni/?endpoint=patroni", "cluster": "/patroni/?endpoint=cluster",
             "history": "/patroni/?endpoint=history", "config": "/patroni/?endpoint=config"}


def fetch_data_from_api(api_url):
    # Construct the path to your CA file
    # ca_file_path = os.path.join(settings.BASE_DIR, 'certs', 'cacert.pem')
    ca_file_path = '/Users/marcusmao/Dev/Test/ca.pem'

    try:
        # Make the GET request, specifying the CA certificate for verification
        response = requests.get(api_url, verify=ca_file_path)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Process the JSON response
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        # Handle request-related errors (e.g., network issues, SSL errors)
        print(f"Error fetching data: {e}")
        return None
    except ValueError as e:
        # Handle JSON decoding errors
        print(f"Error decoding JSON: {e}")
        return None


# Example usage in a Django view:
# from django.shortcuts import render

def patroni_view(request):
    # patroni, cluster, history, config
    endpoint = request.GET.get("endpoint")
    if endpoint is None:
        endpoint = "patroni"

    api_url = "https://192.168.8.51:8008/{}".format(endpoint)
    data = fetch_data_from_api(api_url)
    pretty_json_data = json.dumps(data, indent=4)
    print(pretty_json_data)
    if data:
        return render(request, 'patroni/patroni_status.html',
                      {'data': pretty_json_data, "endpoints": endpoints, "endpoint": endpoint})
    else:
        return render(request, 'patroni/patroni_status.html',
                      {'message': 'Failed to fetch data', "endpoints": "endpoints", "endpoint": endpoint})
