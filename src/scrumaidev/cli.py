from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .runtime_ops import DEFAULT_HARNESS, configure, doctor, uninstall
from .adapters import adapter_catalog, supported_harnesses


def _print_actions(result: dict) -> None:
    print(f"ScrumAIDev {result.get('version', __version__)}")
    if result.get("project"):
        print(f"Project: {result['project']}")
    if result.get("harness"):
        print(f"Harness: {result['harness']}")
    if result.get("runtime_sha256"):
        print(f"Runtime SHA-256: {result['runtime_sha256']}")
    for item in result.get("actions", []):
        print(f"  {item['action']:<24} {item['path']}")
    print(f"Status: {result['status']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scrumaidev", description="ScrumAIDev CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("version", help="Show installed ScrumAIDev CLI/runtime version")

    ad = sub.add_parser("adapters", help="List available harness adapters")
    ad.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    cfg = sub.add_parser("config", help="Configure ScrumAIDev in an existing project")
    cfg.add_argument(
        "--harness",
        choices=supported_harnesses(),
        default=None,
        help=f"Harness to configure (default: the one recorded in the project manifest, otherwise {DEFAULT_HARNESS})",
    )
    cfg.add_argument("--project-dir", default=".")
    cfg.add_argument("--pin", help="Require this exact ScrumAIDev version")
    cfg.add_argument("--dry-run", action="store_true", help="Show planned changes without writing files")
    cfg.add_argument("--force", action="store_true", help="Replace conflicting ScrumAIDev-managed files")
    cfg.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    doc = sub.add_parser("doctor", help="Validate ScrumAIDev configuration")
    doc.add_argument("--project-dir", default=".")
    doc.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    un = sub.add_parser("uninstall", help="Remove ScrumAIDev-managed runtime files")
    un.add_argument("--project-dir", default=".")
    un.add_argument("--dry-run", action="store_true")
    un.add_argument("--force", action="store_true", help="Also remove modified managed files")
    un.add_argument("--purge-seeds", action="store_true", help="Also remove seeded project artifacts")
    un.add_argument("--json", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "version":
            print(__version__)
            return 0
        if args.command == "adapters":
            catalog = adapter_catalog()
            if args.json:
                print(json.dumps(catalog, indent=2, sort_keys=True))
            else:
                print("Available ScrumAIDev harness adapters:")
                for item in catalog:
                    caps = item["capabilities"]
                    delivery = []
                    if caps.get("commands"):
                        delivery.append("commands")
                    if caps.get("skills"):
                        delivery.append("skills")
                    print(f"  {item['id']:<12} {item['display_name']:<24} delivery={'+'.join(delivery) or 'none'}")
            return 0
        if args.command == "config":
            result = configure(Path(args.project_dir), args.harness, args.pin, args.dry_run, args.force)
            if args.json:
                print(json.dumps(result, indent=2, sort_keys=True))
            else:
                _print_actions(result)
            return 0
        if args.command == "doctor":
            result = doctor(Path(args.project_dir))
            if args.json:
                print(json.dumps(result, indent=2, sort_keys=True))
            else:
                print(f"ScrumAIDev doctor - {result['status']}")
                print(f"Project: {result['project']}")
                for warning in result.get("warnings", []):
                    print(f"WARNING: {warning}")
                for error in result.get("errors", []):
                    print(f"ERROR: {error}")
            return 0 if result["status"] == "ok" else 1
        if args.command == "uninstall":
            result = uninstall(Path(args.project_dir), args.dry_run, args.force, args.purge_seeds)
            if args.json:
                print(json.dumps(result, indent=2, sort_keys=True))
            else:
                _print_actions(result)
            return 0
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
