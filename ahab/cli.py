#!/usr/bin/env python3
"""Command-line interface for the ahab API."""

import argparse
import json
import sys

from ahab import job


def _json_body(value):
    try:
        body = json.loads(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be valid JSON") from exc
    if not isinstance(body, dict):
        raise argparse.ArgumentTypeError("must be a JSON object")
    return body


def _add_connection_options(parser):
    parser.add_argument(
        "--api-base-url",
        "--api-url",
        dest="api_base_url",
        help="Function App URL (defaults to AHAB_API_URL)",
    )
    parser.add_argument(
        "--api-key", help="Function key (defaults to AHAB_API_KEY)"
    )


def _build_parser():
    parser = argparse.ArgumentParser(prog="ahab", description="Ahab API client")
    commands = parser.add_subparsers(dest="resource", required=True)

    job_parser = commands.add_parser("job", help="Manage jobs")
    job_actions = job_parser.add_subparsers(dest="action", required=True)
    submit = job_actions.add_parser("submit", help="Create a job")
    submit.add_argument("--body", required=True, type=_json_body)
    listing = job_actions.add_parser("list", help="List jobs without claiming one")
    get = job_actions.add_parser("get", help="List jobs or claim a pending job")
    for action_parser in (listing, get):
        action_parser.add_argument("--job-type", "--job_type")
    update = job_actions.add_parser("update", help="Update a job")
    update.add_argument("--id", required=True)
    update.add_argument("--status", required=True)
    update.add_argument("--body", type=_json_body, default={})
    for action_parser in job_actions.choices.values():
        _add_connection_options(action_parser)

    template_parser = commands.add_parser(
        "job-template", aliases=["job_template"], help="Manage job templates"
    )
    template_actions = template_parser.add_subparsers(dest="action", required=True)
    template_list = template_actions.add_parser("list", help="List job templates")
    template_list.add_argument("--name", help="Return a single template by name")
    for action, description in (
        ("create", "Create a job template"),
        ("update", "Update a job template"),
    ):
        action_parser = template_actions.add_parser(action, help=description)
        action_parser.add_argument("--body", required=True, type=_json_body)
    for action_parser in template_actions.choices.values():
        _add_connection_options(action_parser)
    return parser


def _run(args):
    options = (args.api_base_url or "", args.api_key or "")
    if args.resource == "job":
        if args.action == "submit":
            return job.submit_job(args.body, *options)
        if args.action in ("list", "get"):
            if args.action == "list":
                return job.list_jobs(*options)
            return job.get_job(args.job_type, *options)
        return job.update_job(args.id, args.status, args.body, *options)

    if args.action == "list":
        if args.name:
            return job.get_job_template(args.name, *options)
        return job.list_job_templates(*options)
    if args.action == "create":
        return job.create_job_template(args.body, *options)
    return job.update_job_template(args.body, *options)


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        result = _run(args)
    except (job.AhabApiError, ValueError) as exc:
        print("ahab: {}".format(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def cli():
    """Compatibility entry point used by existing installations."""
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
