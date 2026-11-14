"""Client functions for the ahab job and job-template APIs."""

import os
from urllib.parse import urlsplit, urlunsplit

import requests


class AhabApiError(RuntimeError):
    """Raised when an ahab API request fails."""


def normalize_api_root(api_base_url):
    """Return the API root, accepting either a Function App URL or API URL."""
    candidate = api_base_url.strip()
    if not candidate:
        raise ValueError("API URL is required.")

    parsed = urlsplit(candidate)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("API URL must be an absolute HTTP or HTTPS URL.")

    segments = [segment for segment in parsed.path.split("/") if segment]
    if "api" in segments:
        path = "/" + "/".join(segments[: segments.index("api") + 1])
    else:
        path = parsed.path.rstrip("/") + "/api"
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", "")).rstrip("/")


def _request(method, route, api_base_url, api_key, params=None, body=None):
    api_root = normalize_api_root(api_base_url or os.environ.get("AHAB_API_URL", ""))
    key = api_key or os.environ.get("AHAB_API_KEY", "")
    headers = {"Accept": "application/json"}
    if key:
        headers["x-functions-key"] = key
    kwargs = {"headers": headers, "params": params}
    if body is not None:
        kwargs["json"] = body

    try:
        response = requests.request(
            method, "{}/{}".format(api_root, route.lstrip("/")), **kwargs
        )
    except requests.RequestException as exc:
        raise AhabApiError("Unable to reach the ahab API: {}".format(exc)) from exc

    try:
        payload = response.json()
    except ValueError:
        if response.ok:
            raise AhabApiError("ahab API returned an invalid JSON response.")
        payload = None
    if not response.ok:
        message = payload.get("message") if isinstance(payload, dict) else None
        message = message or response.text.strip() or response.reason
        raise AhabApiError(
            "ahab API request failed ({}): {}".format(response.status_code, message)
        )
    if not isinstance(payload, dict):
        raise AhabApiError("ahab API returned an unexpected response.")
    return payload


def submit_job(body=None, api_base_url="", api_key=""):
    """Create a job using its job_type, metadata, and inputs."""
    return _request(
        "POST", "job", api_base_url, api_key, body={} if body is None else body
    )


def list_jobs(api_base_url="", api_key=""):
    """Return the all-jobs response without claiming a worker job."""
    return _request("GET", "job", api_base_url, api_key)


def get_job(job_type=None, api_base_url="", api_key=""):
    """Claim a pending job of ``job_type``, or list jobs when omitted."""
    params = {"job_type": job_type} if job_type else None
    return _request("GET", "job", api_base_url, api_key, params=params)


def update_job(id="", status="COMPLETE", body=None, api_base_url="", api_key=""):
    """Update a job status and its non-protected fields."""
    return _request(
        "PUT",
        "job",
        api_base_url,
        api_key,
        params={"id": id, "status": status},
        body={} if body is None else body,
    )


def list_job_templates(api_base_url="", api_key=""):
    """List the configured job templates."""
    return _request("GET", "job_template", api_base_url, api_key)


def get_job_template(name, api_base_url="", api_key=""):
    """Get one job template by name."""
    return _request(
        "GET", "job_template", api_base_url, api_key, body={"name": name}
    )


def create_job_template(body=None, api_base_url="", api_key=""):
    """Create a job template."""
    return _request(
        "POST",
        "job_template",
        api_base_url,
        api_key,
        body={} if body is None else body,
    )


def update_job_template(body=None, api_base_url="", api_key=""):
    """Update a job template by its name."""
    return _request(
        "PUT",
        "job_template",
        api_base_url,
        api_key,
        body={} if body is None else body,
    )
