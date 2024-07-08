# ahab - Library 🦑
Library for interacting with the _ahab_ cloud API and Kubernetes system

<h3 align="right">Tuple, LLC | <a href="https://tuple.xyz/solutions/ahab/" target="_blank">tuple.xyz/solutions/ahab/</h3></a>

## Installation
```bash
## Python library from PyPI using pip
pip install ahab-lib

## CLI using pipx
pipx install git+https://github.com/tuplexyz/ahab-lib.git
```

## Environment Variables
This library can use environment variables to avoid passing sensitive information in code.
The following environment variables are used by this library:
- `AHAB_API_URL` - The URL for the _ahab_ cloud API
- `AHAB_API_KEY` - Your API key for the _ahab_ cloud API

You can retrieve these values using the following [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) commands:

```bash
## On Unix
export AHAB_API_URL=https://$(az functionapp show --name func-ahab-dev-eastus-001 --resource-group rg-ahab-dev-eastus-001 --query defaultHostName -o tsv)
export AHAB_API_KEY=$(az functionapp keys list --name func-ahab-dev-eastus-001 --resource-group rg-ahab-dev-eastus-001 --query functionKeys -o tsv)

## On Windows
set AHAB_API_URL=https://$(az functionapp show --name func-ahab-dev-eastus-001 --resource-group rg-ahab-dev-eastus-001 --query defaultHostName -o tsv)
set AHAB_API_KEY=$(az functionapp keys list --name func-ahab-dev-eastus-001 --resource-group rg-ahab-dev-eastus-001 --query functionKeys -o tsv)
```
...changing the `--name` and `--resource-group` values to the names of your _ahab_ instance's Function App and Resource Group, respectively.


## CLI Usage

### Submit Job
```bash
ahab job submit --body='{"job_type": "rnaseq", "metadata": {"project": "project_001", "sample": "sample_001"}, "inputs": {"references": "/mnt/datalake/reference/rnaseq_1", "fastq_1": "/mnt/datalake/project_001/sample_001/rnaseq/file_1.fastq.gz", "fastq_2": "/mnt/datalake/project_001/sample_001/rnaseq/file_2.fastq.gz"}}'
```

### Get Job
```bash
ahab job get --job_type=rnaseq
```

### Update Job
```bash
ahab job update --id=fb273f3b-9665-4f9d-978c-9f6cb9f1cc19 --status=COMPLETE --body='{"outputs": {"bam": "/mnt/datalake/project_001/sample_001/rnaseq/file_1.bam", "bai": "/mnt/datalake/project_001/sample_001/rnaseq/file_1.bam.bai"}}'
```

## Python Usage

### Load in the library and get API information
```python
from ahab.job import get_job, submit_job, update_job
import os, json

api_base_url = os.environ.get('AHAB_API_URL', '')
api_key = os.environ.get('AHAB_API_KEY', '')
```

### Submit Job
```python
body = {
    "job_type": "rnaseq",
    "metadata": {
        "project": "project_001",
        "sample": "sample_001"
    },
    "inputs": {
        "references": "/mnt/datalake/reference/rnaseq_1",
        "fastq_1": "/mnt/datalake/project_001/sample_001/rnaseq/file_1.fastq.gz",
        "fastq_2": "/mnt/datalake/project_001/sample_001/rnaseq/file_2.fastq.gz"
    }
}

response = submit_job(body = body, api_base_url = api_base_url, api_key = api_key)

# {'message': 'Job created successfully.', 'id': 'fb273f3b-9665-4f9d-978c-9f6cb9f1cc19', 'job_type': 'rnaseq'}

```

### Get Job
```python
job = get_job(job_type='rnaseq', api_base_url = api_base_url, api_key = api_key)

# {'id': 'fb273f3b-9665-4f9d-978c-9f6cb9f1cc19', 'job_type': 'rnaseq', 'current_status': 'STARTED', 'status_history': {'2024-04-29T17:10:18.552843': 'PENDING', '2024-04-29T17:11:15.582001': 'STARTED'}, 'metadata': {'project': 'project_001', 'sample': 'sample_001'}, 'inputs': {'references': '/mnt/datalake/reference/rnaseq_1', 'fastq_1': '/mnt/datalake/project_001/sample_001/rnaseq/file_1.fastq.gz', 'fastq_2': '/mnt/datalake/project_001/sample_001/rnaseq/file_2.fastq.gz'}}

```

### Update Job
```python
body = {
    "outputs": {
        "bam": "/mnt/datalake/project_001/sample_001/rnaseq/file_1.bam",
        "bai": "/mnt/datalake/project_001/sample_001/rnaseq/file_1.bam.bai"
    }
}

response = update_job(id = 'fb273f3b-9665-4f9d-978c-9f6cb9f1cc19', status = "COMPLETE", body = body, api_base_url = api_base_url, api_key = api_key)

# {'message': 'Job updated successfully.', 'id': 'fb273f3b-9665-4f9d-978c-9f6cb9f1cc19', 'status': 'COMPLETE'}
```