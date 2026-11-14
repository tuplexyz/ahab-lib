import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from ahab import (
    AhabApiError,
    build_job_body,
    create_job_template,
    get_job,
    get_job_template,
    list_job_templates,
    list_jobs,
    submit_job,
    update_job,
    update_job_template,
)


class JobApiTests(unittest.TestCase):
    def setUp(self):
        self.response = Mock()
        self.response.ok = True
        self.response.json.return_value = {"message": "ok"}

    @patch("ahab.job.requests.request")
    def test_api_root_and_function_key_header(self, request):
        request.return_value = self.response
        list_jobs("https://example.test/workspace/api/job?unused=1", "secret")
        request.assert_called_once_with(
            "GET",
            "https://example.test/workspace/api/job",
            headers={"Accept": "application/json", "x-functions-key": "secret"},
            params=None,
        )

    @patch("ahab.job.requests.request")
    def test_get_job_preserves_claim_behavior_and_lists_without_type(self, request):
        request.return_value = self.response
        get_job("rnaseq", "https://example.test")
        self.assertEqual(request.call_args.kwargs["params"], {"job_type": "rnaseq"})

        request.reset_mock()
        get_job(api_base_url="https://example.test")
        self.assertIsNone(request.call_args.kwargs["params"])

    @patch("ahab.job.requests.request")
    def test_job_mutations_use_updated_api_shapes(self, request):
        request.return_value = self.response
        create_body = {
            "job_type": "rnaseq",
            "metadata": {"sample": "sample-1"},
            "inputs": {"reads": "/data/reads.fastq.gz"},
        }
        submit_job(create_body, "https://example.test")
        self.assertEqual(request.call_args.args[0], "POST")
        self.assertEqual(request.call_args.kwargs["json"], create_body)

        update_body = {"outputs": {"bam": "/data/output.bam"}}
        update_job("job-1", "COMPLETE", update_body, "https://example.test")
        self.assertEqual(request.call_args.args[0], "PUT")
        self.assertEqual(
            request.call_args.kwargs["params"],
            {"id": "job-1", "status": "COMPLETE"},
        )
        self.assertEqual(request.call_args.kwargs["json"], update_body)

    @patch("ahab.job.requests.request")
    def test_submit_job_accepts_structured_fields(self, request):
        request.return_value = self.response
        submit_job(
            api_base_url="https://example.test",
            job_type="rnaseq",
            metadata={"project": "project-1", "sample": "sample-1"},
            inputs={"fastq_1": "/data/reads.fastq.gz"},
        )
        self.assertEqual(
            request.call_args.kwargs["json"],
            {
                "job_type": "rnaseq",
                "metadata": {"project": "project-1", "sample": "sample-1"},
                "inputs": {"fastq_1": "/data/reads.fastq.gz"},
            },
        )

    @patch("ahab.job.requests.request")
    def test_submit_job_accepts_json_file(self, request):
        request.return_value = self.response
        body = {
            "job_type": "rnaseq",
            "metadata": {"sample": "sample-1"},
            "inputs": {"fastq_1": "/data/reads.fastq.gz"},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "job.json"
            path.write_text(json.dumps(body), encoding="utf-8")
            submit_job(
                api_base_url="https://example.test",
                json_file=path,
            )

        self.assertEqual(request.call_args.kwargs["json"], body)

    def test_job_submission_modes_cannot_be_combined(self):
        with self.assertRaisesRegex(ValueError, "only one"):
            build_job_body(
                body={"job_type": "rnaseq", "metadata": {}, "inputs": {}},
                job_type="rnaseq",
            )

    @patch("ahab.job.requests.request")
    def test_job_template_functions_match_endpoint_contract(self, request):
        request.return_value = self.response
        list_job_templates("https://example.test")
        self.assertEqual(request.call_args.args[:2], ("GET", "https://example.test/api/job_template"))
        get_job_template("rnaseq", "https://example.test")
        self.assertEqual(request.call_args.kwargs["json"], {"name": "rnaseq"})
        template = {"name": "rnaseq", "cpu": 0.5}
        create_job_template(template, "https://example.test")
        self.assertEqual(request.call_args.args[0], "POST")
        self.assertEqual(request.call_args.kwargs["json"], template)
        update_job_template(template, "https://example.test")
        self.assertEqual(request.call_args.args[0], "PUT")
        self.assertEqual(request.call_args.kwargs["json"], template)

    @patch("ahab.job.requests.request")
    def test_api_errors_are_raised_with_server_message(self, request):
        self.response.ok = False
        self.response.status_code = 400
        self.response.json.return_value = {"message": "Unknown job type"}
        request.return_value = self.response
        with self.assertRaisesRegex(AhabApiError, "Unknown job type"):
            list_jobs("https://example.test")

    @patch("ahab.job.requests.request")
    def test_invalid_success_response_is_not_returned_as_empty_success(self, request):
        self.response.json.side_effect = ValueError("not JSON")
        request.return_value = self.response
        with self.assertRaisesRegex(AhabApiError, "invalid JSON"):
            list_jobs("https://example.test")


if __name__ == "__main__":
    unittest.main()
