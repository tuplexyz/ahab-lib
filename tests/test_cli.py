import contextlib
import io
import json
import unittest
from unittest.mock import patch

from ahab.cli import main


class CliTests(unittest.TestCase):
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

    def test_invalid_body_is_rejected(self):
        with self.assertRaises(SystemExit) as raised:
            main(["job", "submit", "--body", "[]"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
