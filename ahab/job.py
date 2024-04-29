## Functions for to submit, get, and update jobs in the ahab API
import requests, json, logging

def submit_job(body = {}, api_base_url="", api_key=""):
    api_url = f'{api_base_url}/api/job?code={api_key}'
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", api_url, headers=headers, data=json.dumps(body))
    if response.status_code >= 300:
        logging.error(f"Failed to submit job: {response.json()}")
    else:
        logging.info(f"Job submitted: {response.json()}")
    return response.json()

def get_job(job_type="demo", api_base_url="", api_key=""):
    api_url = f'{api_base_url}/api/job?code={api_key}&job_type={job_type}'
    response = requests.request("GET", api_url, headers={}, data={})
    if response.status_code != 200:
        logging.error(f"Failed to get job: {response.json()}")
    else:
        logging.info(f"Job retrieved: {response.json()}")
    return response.json()

def update_job(id="", status="COMPLETE", body={}, api_base_url="", api_key=""):
    api_url = f'{api_base_url}/api/job?code={api_key}&id={id}&status={status}'
    headers = {'Content-Type': 'application/json'}
    response = requests.request("PUT", api_url, headers=headers, data=json.dumps(body))
    if response.status_code != 200:
        logging.error(f"Failed to update job: {response.json()}")
    else:
        logging.info(f"Job updated: {response.json()}")
    return response.json()

