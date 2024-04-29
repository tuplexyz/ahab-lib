## A Python package and CLI to integrate with the `ahab` API

import os, json
from ahab.job import get_job, submit_job, update_job
from cleo.commands.command import Command
from cleo.helpers import argument, option

class JobCommand(Command):

    name = "job"
    description = "Submit/Get/Update a job with the `ahab` API"

    arguments = [
        argument(
            "action",
            description="The action to run",
            optional=True
        )
    ]

    options = [
        option(
            "body",
            "b",
            description="The body of the job to submit/update (as a <comment>JSON</comment> string)",
            flag=False
        ),
        option(
            "job_type",
            "j",
            description="The job type from which to query a job with a `PENDING` status",
            flag=False
        ),
        option(
            "id",
            None,
            description="The ID of the job to run",
            flag=False
        ),
        option(
            "status",
            "s",
            description="The new status to be set for the job",
            flag=False
        ),
        option(
            "api_base_url",
            "u",
            description = "The base URL of the <fg=magenta>ahab</> Function API (e.g., <comment>https://func-ahab-dev-eastus-001.azurewebsites.net</comment>).\nIf not provided, the value of the <comment>AHAB_API_URL</comment> environment variable will be used.",
            flag=False
        ),
        option(
            "api_key",
            "k",
            description = "The key of the <fg=magenta>ahab</> Function API (e.g., <comment>DmXPlzmZ3Pq2chtVV_gggzVKh2uAIlFIGgcr9nkl29U0AzFuToWgIw==</comment>).\nIf not provided, the value of the <comment>AHAB_API_KEY</comment> environment variable will be used.",
            flag=False
        )
    ]

    def handle(self):
        ## Get URL and key for API
        if self.option('api_base_url') and self.option('api_key'):
            api_base_url = self.option('api_base_url')
            api_key = self.option('api_key')
        elif 'AHAB_API_URL' and 'AHAB_API_KEY' not in os.environ:
            self.line('Your <fg=magenta>ahab</> API URL and key must be defined in the environment as <comment>AHAB_API_URL</comment> and <comment>AHAB_API_KEY</comment>, respectively.')
            return
        else:
            api_base_url = os.environ.get('AHAB_API_URL', '')
            api_key = os.environ.get('AHAB_API_KEY', '')

        action = self.argument('action')

        ## Submit Job
        if action == 'submit':
            body = json.loads(self.option('body'))
            ## Check keys in body
            if set(['job_type']).issubset(set(body.keys())):
                response = submit_job(body, api_base_url, api_key)
                self.line(json.dumps(response))
            else:
                self.line('You must provide a job type for the job to submit.')
                return
            

        ## Get Job
        if action == 'get':
            job_type = self.option('job_type')
            response = get_job(job_type, api_base_url, api_key)
            self.line(json.dumps(response))

        ## Update Job
        if action == 'update':
            id = self.option('id')
            status = self.option('status')
            body = json.loads(self.option('body'))
            response = update_job(id, status, body, api_base_url, api_key)
            self.line(json.dumps(response))