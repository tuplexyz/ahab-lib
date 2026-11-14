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

The CLI is installed with the package and reads `AHAB_API_URL` and
`AHAB_API_KEY` from the environment by default. Per-command `--api-base-url`
and `--api-key` options can override them.

### Submit, list, claim, and update jobs
```bash
ahab job submit --body='{"job_type": "rnaseq", "metadata": {"project": "project_001", "sample": "sample_001"}, "inputs": {"references": "/mnt/datalake/reference/rnaseq_1", "fastq_1": "/mnt/datalake/project_001/sample_001/rnaseq/file_1.fastq.gz", "fastq_2": "/mnt/datalake/project_001/sample_001/rnaseq/file_2.fastq.gz"}}'
# List every job without claiming or changing its status
ahab job list
# Claim a pending job for a worker (the API changes it to STARTED)
ahab job get --job_type=rnaseq
ahab job update --id=fb273f3b-9665-4f9d-978c-9f6cb9f1cc19 --status=COMPLETE --body='{"outputs": {"bam": "/mnt/datalake/project_001/sample_001/rnaseq/file_1.bam", "bai": "/mnt/datalake/project_001/sample_001/rnaseq/file_1.bam.bai"}}'
```

### Manage job templates
```bash
ahab job-template list
ahab job-template list --name=rnaseq
ahab job-template create --body='{"name":"rnaseq","pool_name":"rnaseq","image":"example/worker:latest","max_nodes":1,"vm_size":"Standard_D4s_v5","memory":"8Gi","cpu":2,"command":["/bin/bash"],"args":["run.sh"]}'
ahab job-template update --body='{"name":"rnaseq","image":"example/worker:v2"}'
```

## Python Usage

### Submit, list, and update jobs
```python
from ahab import list_jobs, get_job, submit_job, update_job

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

response = submit_job(body)

# {'message': 'Job created successfully.', 'id': 'fb273f3b-9665-4f9d-978c-9f6cb9f1cc19', 'job_type': 'rnaseq'}

# List all jobs without changing status.
jobs = list_jobs()

# Worker claim: returns one pending job and changes its status to STARTED.
job = get_job(job_type="rnaseq")

update_job(
    id=job["id"],
    status="COMPLETE",
    body={"outputs": {"bam": "/mnt/results/sample.bam"}},
)

# Explicit credentials are optional; AHAB_API_URL and AHAB_API_KEY are used by default.
# Functions also accept api_base_url="..." and api_key="...".
```

### Manage job templates
```python
from ahab import list_job_templates, get_job_template, create_job_template, update_job_template

templates = list_job_templates()
rnaseq = get_job_template("rnaseq")
create_job_template({
    "name": "variant-calling",
    "pool_name": "rnaseq",
    "image": "example/worker:latest",
    "max_nodes": 1,
    "vm_size": "Standard_D4s_v5",
    "memory": "8Gi",
    "cpu": 2,
    "command": ["/bin/bash"],
    "args": ["run.sh"],
})
update_job_template({"name": "rnaseq", "image": "example/worker:v2"})
```
