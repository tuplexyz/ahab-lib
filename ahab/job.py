"""Client functions for the ahab job and job-template APIs."""

import json
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


def _validate_job_body(body):
    if not isinstance(body, dict):
        raise ValueError("Job body must be a JSON object.")

    missing_fields = [
        field for field in ("job_type", "metadata", "inputs") if field not in body
    ]
    if missing_fields:
        raise ValueError(
            "Job body is missing required field(s): {}".format(missing_fields)
        )
    if not isinstance(body["job_type"], str) or not body["job_type"].strip():
        raise ValueError("job_type must be a non-empty string.")
    if not isinstance(body["metadata"], dict):
        raise ValueError("metadata must be a dictionary.")
    if not isinstance(body["inputs"], dict):
        raise ValueError("inputs must be a dictionary.")
    return body


def _load_job_body(json_file):
    try:
        with open(json_file, encoding="utf-8") as file_handle:
            body = json.load(file_handle)
    except OSError as exc:
        raise ValueError(
            "Unable to read job JSON file '{}': {}".format(json_file, exc)
        ) from exc
    except ValueError as exc:
        raise ValueError(
            "Job JSON file '{}' must contain valid JSON.".format(json_file)
        ) from exc
    return _validate_job_body(body)


def build_job_body(
    body=None,
    job_type=None,
    metadata=None,
    inputs=None,
    json_file=None,
):
    """Build and validate a job request from one supported input mode."""
    structured = any(
        value is not None for value in (job_type, metadata, inputs)
    )
    modes = sum((body is not None, json_file is not None, structured))
    if modes == 0:
        raise ValueError(
            "Provide a job body, a JSON file, or job_type with metadata and inputs."
        )
    if modes > 1:
        raise ValueError(
            "Use only one job submission mode: body, JSON file, or structured fields."
        )

    if body is not None:
        return _validate_job_body(body)
    if json_file is not None:
        return _load_job_body(json_file)
    if not isinstance(job_type, str) or not job_type.strip():
        raise ValueError("job_type is required for structured job submission.")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary.")
    if inputs is not None and not isinstance(inputs, dict):
        raise ValueError("inputs must be a dictionary.")
    return {
        "job_type": job_type,
        "metadata": {} if metadata is None else metadata,
        "inputs": {} if inputs is None else inputs,
    }


def submit_job(
    body=None,
    api_base_url="",
    api_key="",
    job_type=None,
    metadata=None,
    inputs=None,
    json_file=None,
):
    """Create a job from a body, JSON file, or structured fields."""
    job_body = build_job_body(
        body=body,
        job_type=job_type,
        metadata=metadata,
        inputs=inputs,
        json_file=json_file,
    )
    return _request("POST", "job", api_base_url, api_key, body=job_body)


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
