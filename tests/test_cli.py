import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ahab.cli import main


class CliTests(unittest.TestCase):
    def test_cli_reports_package_version(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as raised:
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(output.getvalue().strip(), "ahab 1.1.0")

    def test_job_list_calls_non_claiming_operation(self):
        output = io.StringIO()
        with patch("ahab.cli.job.list_jobs", return_value={"jobs": []}) as list_jobs:
            with contextlib.redirect_stdout(output):
                result = main(["job", "list"])

        self.assertEqual(result, 0)
        list_jobs.assert_called_once_with("", "")
        self.assertEqual(json.loads(output.getvalue()), {"jobs": []})

    def test_template_create_passes_json_object(self):
        output = io.StringIO()
        template = {"name": "rnaseq", "cpu": 0.5}
        with patch(
            "ahab.cli.job.create_job_template", return_value={"id": "template-1"}
        ) as create:
            with contextlib.redirect_stdout(output):
                result = main(
                    [
                        "job-template",
                        "create",
                        "--body",
                        json.dumps(template),
                        "--api-base-url",
                        "https://example.test",
                    ]
                )

        self.assertEqual(result, 0)
        create.assert_called_once_with(template, "https://example.test", "")

    def test_job_submit_accepts_structured_flags(self):
        output = io.StringIO()
        with patch(
            "ahab.cli.job.submit_job", return_value={"id": "job-1"}
        ) as submit:
            with contextlib.redirect_stdout(output):
                result = main(
                    [
                        "job",
                        "submit",
                        "--job-type",
                        "rnaseq",
                        "--metadata",
                        "project=project_001",
                        "--metadata",
                        "sample=sample_001",
                        "--input",
                        "fastq_1=/data/reads_1.fastq.gz",
                        "--input",
                        "fastq_2=/data/reads_2.fastq.gz",
                    ]
                )

        self.assertEqual(result, 0)
        submit.assert_called_once_with(
            body=None,
            api_base_url="",
            api_key="",
            job_type="rnaseq",
            metadata={"project": "project_001", "sample": "sample_001"},
            inputs={
                "fastq_1": "/data/reads_1.fastq.gz",
                "fastq_2": "/data/reads_2.fastq.gz",
            },
            json_file=None,
        )

    def test_job_submit_accepts_body_and_json_file_modes(self):
        body = {"job_type": "rnaseq", "metadata": {}, "inputs": {}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "job.json"
            path.write_text(json.dumps(body), encoding="utf-8")
            for arguments, expected in (
                (["--body", json.dumps(body)], {"body": body, "json_file": None}),
                (["--file", str(path)], {"body": None, "json_file": str(path)}),
            ):
                with self.subTest(arguments=arguments), patch(
                    "ahab.cli.job.submit_job", return_value={"id": "job-1"}
                ) as submit, contextlib.redirect_stdout(io.StringIO()):
                    result = main(["job", "submit"] + arguments)

                self.assertEqual(result, 0)
                self.assertEqual(submit.call_args.kwargs["body"], expected["body"])
                self.assertEqual(
                    submit.call_args.kwargs["json_file"], expected["json_file"]
                )

    def test_invalid_body_is_rejected(self):
        with self.assertRaises(SystemExit) as raised:
            main(["job", "submit", "--body", "[]"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
