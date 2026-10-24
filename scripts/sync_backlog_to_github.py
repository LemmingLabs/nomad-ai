#!/usr/bin/env python3
"""Idempotently sync planning/backlog Markdown issues and milestones with GitHub."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKLOG_DIR = ROOT / "planning" / "backlog"
MANIFEST_PATH = BACKLOG_DIR / "backlog.json"
ISSUE_MARKER_RE = re.compile(r"<!--\s*backlog-id:\s*([A-Z0-9-]+)\s*-->")
ISSUE_URL_RE = re.compile(r"https://[^\s]+/issues/(\d+)")


class SyncError(RuntimeError):
    pass


def gh(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["gh", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise SyncError(f"gh {' '.join(args[:4])} failed: {message}")
    return result.stdout.strip()


def load_manifest() -> dict[str, Any]:
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"Cannot read backlog manifest: {exc}") from exc

    milestones = manifest.get("milestones", [])
    issues = manifest.get("issues", [])
    ids = [item.get("id") for item in issues]
    if not ids or len(ids) != len(set(ids)):
        raise SyncError("Issue IDs must be present and unique in backlog.json")

    milestone_ids = {item.get("id") for item in milestones}
    issue_ids = set(ids)
    for item in issues:
        if item.get("milestone") not in milestone_ids:
            raise SyncError(f"{item['id']} refers to an unknown milestone")
        body_file = BACKLOG_DIR / item.get("file", "")
        if not body_file.is_file():
            raise SyncError(f"{item['id']} body file is missing: {body_file}")
        for dependency in item.get("depends_on", []):
            if dependency not in issue_ids:
                raise SyncError(f"{item['id']} refers to an unknown dependency: {dependency}")
        for child in item.get("children", []):
            if child not in issue_ids:
                raise SyncError(f"{item['id']} refers to an unknown child: {child}")

    for item in issues:
        if item.get("kind") == "epic" and any(
            next(candidate for candidate in issues if candidate["id"] == child).get("kind") == "epic"
            for child in item.get("children", [])
        ):
            raise SyncError(f"Epic {item['id']} cannot contain another epic")

    return manifest


def resolve_repo(explicit_repo: str | None) -> str:
    repo = explicit_repo or os.environ.get("GITHUB_REPOSITORY")
    if repo:
        return repo
    return gh("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")


def read_existing_milestones(repo: str) -> dict[str, dict[str, Any]]:
    output = gh(
        "api",
        "--paginate",
        f"repos/{repo}/milestones?state=all&per_page=100",
    )
    try:
        values = json.loads(output)
    except json.JSONDecodeError as exc:
        raise SyncError(f"GitHub returned invalid milestone JSON: {exc}") from exc
    return {item["title"]: item for item in values}


def read_existing_labels(repo: str) -> set[str]:
    output = gh("label", "list", "--repo", repo, "--limit", "500", "--json", "name")
    return {item["name"] for item in json.loads(output)}


def read_existing_issues(repo: str) -> dict[str, dict[str, Any]]:
    output = gh(
        "issue",
        "list",
        "--repo",
        repo,
        "--state",
        "all",
        "--limit",
        "1000",
        "--json",
        "number,title,body,url,milestone,labels",
    )
    issues = json.loads(output)
    found: dict[str, dict[str, Any]] = {}
    for issue in issues:
        for marker in ISSUE_MARKER_RE.findall(issue.get("body") or ""):
            if marker in found:
                raise SyncError(f"More than one GitHub issue has backlog-id {marker}")
            found[marker] = issue
    return found


def ensure_milestones(
    repo: str,
    manifest: dict[str, Any],
    dry_run: bool,
    existing: dict[str, dict[str, Any]],
) -> None:
    for milestone in manifest["milestones"]:
        current = existing.get(milestone["title"])
        if current and current.get("state") == "open":
            print(f"OK milestone: {milestone['title']} (#{current['number']})")
            continue
        if current:
            print(f"OPEN milestone: {milestone['title']} (#{current['number']})")
            if not dry_run:
                gh(
                    "api",
                    f"repos/{repo}/milestones/{current['number']}",
                    "-X",
                    "PATCH",
                    "-F",
                    "state=open",
                )
            continue
        print(f"CREATE milestone: {milestone['title']}")
        if not dry_run:
            gh(
                "api",
                f"repos/{repo}/milestones",
                "-X",
                "POST",
                "-f",
                f"title={milestone['title']}",
                "-f",
                f"description={milestone['description']}",
            )


def ensure_labels(repo: str, manifest: dict[str, Any], dry_run: bool, existing: set[str]) -> None:
    for label in manifest.get("labels", []):
        if label["name"] in existing:
            print(f"OK label: {label['name']}")
            continue
        print(f"CREATE label: {label['name']}")
        if not dry_run:
            gh(
                "label",
                "create",
                label["name"],
                "--repo",
                repo,
                "--color",
                label["color"],
                "--description",
                label["description"],
            )


def render_body(
    item: dict[str, Any],
    issues_by_id: dict[str, dict[str, Any]],
    items_by_id: dict[str, dict[str, Any]],
    with_children: bool = False,
) -> str:
    source_path = BACKLOG_DIR / item["file"]
    source = source_path.read_text(encoding="utf-8").strip()
    marker = f"<!-- backlog-id: {item['id']} -->"
    body = f"{marker}\n\n{source}"

    parent = next(
        (candidate for candidate in items_by_id.values() if item["id"] in candidate.get("children", [])),
        None,
    )
    if parent:
        target = issues_by_id.get(parent["id"])
        number = target.get("number") if target else None
        label = f"#{number} — {parent['title']}" if number else f"{parent['id']} — {parent['title']}"
        body += f"\n\n## Epic\n\nTracked under {label}."

    dependencies = item.get("depends_on", [])
    if dependencies:
        lines = ["\n\n## Backlog dependencies"]
        for dependency in dependencies:
            target = issues_by_id.get(dependency)
            number = target.get("number") if target else None
            label = items_by_id[dependency]["title"]
            lines.append(f"- #{number} — {label}" if number else f"- {dependency} — {label}")
        body += "\n".join(lines)

    if with_children:
        children = item.get("children", [])
        lines = ["\n\n## Child issues"]
        for child_id in children:
            target = issues_by_id.get(child_id)
            number = target.get("number") if target else None
            label = items_by_id[child_id]["title"]
            lines.append(f"- [ ] #{number} — {label}" if number else f"- [ ] {child_id} — {label}")
        body += "\n".join(lines)
    return body.strip() + "\n"


def mutate_issue(
    repo: str,
    item: dict[str, Any],
    body: str,
    milestone_title: str,
    existing: dict[str, Any] | None,
    dry_run: bool,
) -> dict[str, Any] | None:
    labels = ["roadmap", "epic" if item["kind"] == "epic" else "enhancement"]
    milestone = existing.get("milestone") if existing else None
    existing_labels = {label["name"] for label in existing.get("labels", [])} if existing else set()
    needs_update = bool(
        existing
        and (
            existing.get("title") != item["title"]
            or (existing.get("body") or "").strip() != body.strip()
            or (milestone or {}).get("title") != milestone_title
            or not set(labels).issubset(existing_labels)
        )
    )
    action = "UPDATE" if needs_update else "CREATE" if not existing else "OK"
    number_label = f"#{existing['number']}" if existing else ""
    print(f"{action} issue {item['id']} {number_label}: {item['title']} [{milestone_title}]")
    if dry_run:
        return existing
    if existing and not needs_update:
        return existing

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".md") as body_file:
        body_file.write(body)
        body_file.flush()
        if existing:
            args = [
                "issue",
                "edit",
                str(existing["number"]),
                "--repo",
                repo,
                "--title",
                item["title"],
                "--body-file",
                body_file.name,
                "--milestone",
                milestone_title,
            ]
            for label in labels:
                args.extend(["--add-label", label])
            gh(*args)
            return {**existing, "title": item["title"], "body": body}

        args = [
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            item["title"],
            "--body-file",
            body_file.name,
            "--milestone",
            milestone_title,
        ]
        for label in labels:
            args.extend(["--label", label])
        output = gh(*args)
    match = ISSUE_URL_RE.search(output)
    if not match:
        raise SyncError(f"Could not read created issue URL for {item['id']}: {output}")
    return {"number": int(match.group(1)), "title": item["title"], "body": body, "url": output}


def sync_issues(
    repo: str,
    manifest: dict[str, Any],
    existing: dict[str, dict[str, Any]],
    dry_run: bool,
) -> None:
    items = manifest["issues"]
    items_by_id = {item["id"]: item for item in items}
    issues_by_id: dict[str, dict[str, Any]] = dict(existing)
    epics = [item for item in items if item["kind"] == "epic"]
    tasks = [item for item in items if item["kind"] != "epic"]

    # Create/update parents first so every child is associated with a known epic.
    for item in epics:
        milestone = next(value for value in manifest["milestones"] if value["id"] == item["milestone"])
        children = item.get("children", [])
        has_all_children = all(child_id in issues_by_id for child_id in children)
        issue = mutate_issue(
            repo,
            item,
            render_body(item, issues_by_id, items_by_id, with_children=has_all_children),
            milestone["title"],
            existing.get(item["id"]),
            dry_run,
        )
        if issue:
            issues_by_id[item["id"]] = issue

    for item in tasks:
        milestone = next(value for value in manifest["milestones"] if value["id"] == item["milestone"])
        issue = mutate_issue(
            repo,
            item,
            render_body(item, issues_by_id, items_by_id),
            milestone["title"],
            existing.get(item["id"]),
            dry_run,
        )
        if issue:
            issues_by_id[item["id"]] = issue

    # Re-render parent checklists now that all child issue numbers are known.
    for item in epics:
        milestone = next(value for value in manifest["milestones"] if value["id"] == item["milestone"])
        mutate_issue(
            repo,
            item,
            render_body(item, issues_by_id, items_by_id, with_children=True),
            milestone["title"],
            issues_by_id.get(item["id"]),
            dry_run,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="show planned mutations without writing to GitHub")
    parser.add_argument("--repo", help="GitHub repository in OWNER/NAME form; defaults to the current remote")
    args = parser.parse_args()

    try:
        manifest = load_manifest()
        repo = resolve_repo(args.repo)
        print(f"Backlog target: {repo}")
        milestone_state = read_existing_milestones(repo)
        label_state = read_existing_labels(repo)
        issue_state = read_existing_issues(repo)
        ensure_milestones(repo, manifest, args.dry_run, milestone_state)
        ensure_labels(repo, manifest, args.dry_run, label_state)
        sync_issues(repo, manifest, issue_state, args.dry_run)
        if args.dry_run:
            print("Dry run complete. No GitHub resources were changed.")
        else:
            print("Backlog sync complete.")
    except (SyncError, json.JSONDecodeError, OSError, StopIteration) as exc:
        print(f"Backlog sync failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
