#!/usr/bin/env python3
"""Automated live validation of the ScrumAIDev Claude Code adapter.

Maintainer-only. NOT part of the runtime payload and NOT run by CI: it drives
the real Claude Code CLI in headless mode (`claude -p`), which consumes model
tokens on the account that is logged in.

It configures throwaway projects with the installed `scrumaidev` CLI and
checks, against the real harness:

  C1  discovery of every `scrumaidev-*` skill (deterministic: session init);
  C2  `.claude/rules/scrumaidev.md` loaded and `@../../AGENTS.md` expanded,
      in a greenfield project and in a brownfield project with its own
      `CLAUDE.md`;
  C3  `/scrumaidev-scope-idea <args>`: arguments reach the skill, the
      canonical workflow is read, and the flow stops at the human gate
      (no Discovery/Requirements/Story artifacts written);
  C4  a specialist facade (`scrumaidev-architect`) is used and reads the
      canonical `.agents/skills/architect/SKILL.md`;
  C5  workflow skills are not model-invocable (the harness refuses the attempt);
  C6  the main-loop model never changes while ScrumAIDev skills run;
  C7  no AI `Co-authored-by:` trailer in a proposed commit message.

C3-C5 and C7 exercise model behavior and are therefore probabilistic; the
report keeps the raw evidence (tool calls and final text) for human audit.
The VS Code UI itself (the `/` menu, the model selector) is not covered.

Usage:
    python scripts/live_validate_claude.py [--scrumaidev scrumaidev] [--claude claude]
        [--workdir DIR] [--model MODEL] [--keep]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WORKFLOWS = (
    "code-review", "create-user-story", "deploy", "discover", "e2e-test",
    "feature-development", "init-project", "integrate-backend",
    "publish-github-planning", "requirements", "scope-idea", "sprint-planning",
    "sprint-retrospective",
)
SPECIALISTS = (
    "architect", "backend-python", "frontend-vue", "qa-engineer", "react-expert",
    "security-expert", "skill-creator", "story-refiner", "technical-writer",
)
AGENTS_HEADING = "# AGENTS.md — Contrato Operacional do Agente"
ARG_TOKEN = "ZX7-TAREFAS"
NO_TOOLS = "Read Glob Grep Bash Write Edit Skill Agent WebFetch WebSearch NotebookEdit"
# Nested runs (e.g. from inside a Claude Code session) must not inherit the
# parent session identity.
PARENT_ENV = (
    "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_MESSAGING_SOCKET",
    "CLAUDE_CODE_MESSAGING_TOKEN", "CLAUDE_CODE_SESSION_ATTENDED",
)


def run(cmd: list[str], cwd: Path, timeout: int = 900) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in PARENT_ENV}
    return subprocess.run(
        cmd, cwd=cwd, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )


class Claude:
    def __init__(self, exe: str, model: str | None):
        self.exe = exe
        self.model = model
        self.cost = 0.0

    def ask(self, project: Path, prompt: str, *, allowed: str = "", disallowed: str = "",
            max_turns: int = 20) -> dict:
        cmd = [self.exe, "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--max-turns", str(max_turns)]
        if self.model:
            cmd += ["--model", self.model]
        if allowed:
            cmd += ["--allowedTools", allowed]
        if disallowed:
            cmd += ["--disallowedTools", disallowed]
        started = time.time()
        proc = run(cmd, project)
        events = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
        result = next((e for e in reversed(events) if e.get("type") == "result"), {})
        self.cost += float(result.get("total_cost_usd") or 0)
        tool_uses = []
        tool_results = {}
        assistant_models = []
        for e in events:
            msg = e.get("message") or {}
            blocks = [b for b in (msg.get("content") or []) if isinstance(b, dict)]
            if e.get("type") == "user":
                for block in blocks:
                    if block.get("type") == "tool_result":
                        tool_results[block.get("tool_use_id")] = {
                            "is_error": bool(block.get("is_error")),
                            "content": str(block.get("content"))[:300],
                        }
            if e.get("type") != "assistant":
                continue
            if msg.get("model"):
                assistant_models.append(msg["model"])
            for block in blocks:
                if block.get("type") == "tool_use":
                    tool_uses.append({"id": block.get("id"), "name": block.get("name"), "input": block.get("input")})
        for use in tool_uses:
            use["result"] = tool_results.get(use.pop("id"), {})
        return {
            "exit": proc.returncode,
            "stderr": proc.stderr[-2000:],
            "seconds": round(time.time() - started, 1),
            "init": init,
            "result_text": result.get("result") or "",
            "result_subtype": result.get("subtype"),
            "num_turns": result.get("num_turns"),
            "model_usage": sorted((result.get("modelUsage") or {}).keys()),
            "assistant_models": sorted(set(assistant_models)),
            "tool_uses": tool_uses,
            "raw": proc.stdout,
        }


def snapshot(project: Path) -> set[str]:
    return {
        p.relative_to(project).as_posix()
        for p in project.rglob("*")
        if p.is_file() and ".git" not in p.relative_to(project).parts
    }


def make_project(scrumaidev: str, root: Path, name: str, brownfield: bool) -> Path:
    project = root / name
    project.mkdir(parents=True)
    run(["git", "init", "-q"], project)
    if brownfield:
        (project / "CLAUDE.md").write_text(
            "# Existing project instructions\n\nThis project already had its own CLAUDE.md.\n",
            encoding="utf-8",
        )
        (project / ".claude").mkdir()
        (project / ".claude/settings.json").write_text('{"permissions": {"allow": []}}\n', encoding="utf-8")
    version = run([scrumaidev, "version"], project).stdout.strip()
    cfg = run([scrumaidev, "config", "--harness", "claude", "--pin", version], project)
    if cfg.returncode != 0:
        raise SystemExit(f"scrumaidev config failed in {project}:\n{cfg.stderr}")
    doc = run([scrumaidev, "doctor"], project)
    if doc.returncode != 0:
        raise SystemExit(f"scrumaidev doctor failed in {project}:\n{doc.stdout}{doc.stderr}")
    return project


def skill_calls(r: dict) -> list[str]:
    return [str((t["input"] or {}).get("skill", "")) for t in r["tool_uses"] if t["name"] == "Skill"]


def skill_attempts(r: dict) -> list[dict]:
    return [
        {"skill": str((t["input"] or {}).get("skill", "")), "result": t.get("result", {})}
        for t in r["tool_uses"] if t["name"] == "Skill"
    ]


def read_paths(r: dict) -> list[str]:
    return [str((t["input"] or {}).get("file_path", "")).replace("\\", "/")
            for t in r["tool_uses"] if t["name"] == "Read"]


def check(checks: list, cid: str, title: str, ok: bool, evidence: dict) -> None:
    checks.append({"id": cid, "title": title, "status": "PASS" if ok else "FAIL", "evidence": evidence})
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {title}", flush=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scrumaidev", default="scrumaidev")
    ap.add_argument("--claude", default="claude")
    ap.add_argument("--workdir", default="")
    ap.add_argument("--model", default="", help="optional; default is the account/session default model")
    ap.add_argument("--keep", action="store_true", help="keep the throwaway projects")
    args = ap.parse_args(argv)

    for exe in (args.scrumaidev, args.claude):
        if not shutil.which(exe) and not Path(exe).exists():
            raise SystemExit(f"executable not found: {exe}")

    root = Path(args.workdir or tempfile.mkdtemp(prefix="scrumaidev-live-"))
    root.mkdir(parents=True, exist_ok=True)
    claude = Claude(args.claude, args.model or None)
    checks: list[dict] = []
    runs: dict[str, dict] = {}

    print(f"Workdir: {root}", flush=True)
    green = make_project(args.scrumaidev, root, "greenfield", brownfield=False)
    brown = make_project(args.scrumaidev, root, "brownfield", brownfield=True)
    versions = {
        "scrumaidev": run([args.scrumaidev, "version"], green).stdout.strip(),
        "claude_cli": run([args.claude, "--version"], green).stdout.strip(),
    }
    print(f"Versions: {versions}", flush=True)

    # C1 + C2 (greenfield): deterministic init data + context question without tools.
    context_prompt = (
        "Answer ONLY from the instructions already in your context. Do not use any tool. "
        "Reply with exactly one JSON object and nothing else: "
        '{"scrumaidev_rule_loaded": <true if a project rule saying it was generated by '
        '`scrumaidev config --harness claude` is in your context>, '
        '"agents_md_heading": "<the first Markdown heading line of the AGENTS.md content in your '
        'context, verbatim, or NOT_IN_CONTEXT>"}'
    )
    for label, project in (("greenfield", green), ("brownfield", brown)):
        r = claude.ask(project, context_prompt, disallowed=NO_TOOLS, max_turns=2)
        runs[f"context-{label}"] = r
        init = r["init"]
        if label == "greenfield":
            slash = set(init.get("slash_commands") or [])
            skills = set(init.get("skills") or [])
            expected = {f"scrumaidev-{w}" for w in WORKFLOWS} | {f"scrumaidev-{s}" for s in SPECIALISTS}
            check(checks, "C1", "all 22 scrumaidev-* skills discovered by Claude Code (slash commands + skill inventory)",
                  expected <= slash and expected <= skills,
                  {"missing_slash": sorted(expected - slash), "missing_skills": sorted(expected - skills),
                   "discovered": sorted(n for n in slash if n.startswith("scrumaidev-"))})
        answer = {}
        text = r["result_text"].strip()
        try:
            answer = json.loads(text[text.find("{"): text.rfind("}") + 1])
        except (ValueError, json.JSONDecodeError):
            pass
        check(checks, f"C2-{label}",
              f"project rule loaded and AGENTS.md imported into context ({label})",
              answer.get("scrumaidev_rule_loaded") is True
              and str(answer.get("agents_md_heading", "")).strip() == AGENTS_HEADING
              and not r["tool_uses"],
              {"answer": answer or text[:500], "tool_uses": r["tool_uses"],
               "memory_paths": r["init"].get("memory_paths")})

    # C3: workflow invocation, arguments, canonical read, human gate.
    before = snapshot(green)
    idea = (f"Quero criar um pequeno sistema ({ARG_TOKEN}) para alunos registrarem tarefas "
            "de um projeto com titulo, responsavel, status e prazo.")
    r = claude.ask(green, f"/scrumaidev-scope-idea {idea}", allowed="Read Glob Grep Write Edit", max_turns=25)
    runs["scope-idea"] = r
    created = sorted(snapshot(green) - before)
    gated_artifacts = [p for p in created if p.startswith(("docs/discovery/", "docs/requirements/",
                                                            "docs/stories/", "docs/sprints/"))]
    text = r["result_text"]
    upper = text.upper()
    arg_seen = ARG_TOKEN in r["raw"]
    canonical_read = any(p.endswith(".agents/workflows/scope-idea.md") for p in read_paths(r))
    classified = any(k in upper for k in ("LIGHT PROCESS", "NORMAL PROCESS", "HEAVY PROCESS"))
    asks_review = ("C0" in upper or "REVIEW" in upper or "?" in text)
    check(checks, "C3a", "/scrumaidev-scope-idea receives the user arguments", arg_seen,
          {"token": ARG_TOKEN})
    check(checks, "C3b", "facade reads the canonical .agents/workflows/scope-idea.md", canonical_read,
          {"reads": read_paths(r)})
    check(checks, "C3c", "flow stops at CHECKPOINT C0 (classification proposed, review requested, no gated artifacts)",
          classified and asks_review and not gated_artifacts and r["result_subtype"] == "success",
          {"created_files": created, "gated_artifacts": gated_artifacts,
           "result_subtype": r["result_subtype"], "num_turns": r["num_turns"],
           "final_text_excerpt": text[:1500]})

    # C4: specialist facade.
    r = claude.ask(
        green,
        "Precisamos decidir, neste projeto, entre envio sincrono de e-mails pela API e uma fila "
        "(Redis/RabbitMQ) para notificacoes. Use a skill especialista mais adequada deste projeto "
        "e responda com uma recomendacao curta. Nao crie nem altere arquivos.",
        allowed="Skill Read Glob Grep", max_turns=10,
    )
    runs["specialist"] = r
    calls = skill_calls(r)
    check(checks, "C4", "Claude uses scrumaidev-architect, which reads the canonical architect SKILL.md",
          any(c.endswith("scrumaidev-architect") for c in calls)
          and any(p.endswith(".agents/skills/architect/SKILL.md") for p in read_paths(r)),
          {"skill_calls": calls, "reads": read_paths(r)})

    # C5: the model must not self-invoke a workflow skill. An attempt is fine
    # only if the harness refuses it (disable-model-invocation).
    r = claude.ask(
        green,
        "Inicie o workflow ScrumAIDev scope-idea para esta ideia: um mural de avisos para a turma. "
        "Pare no primeiro checkpoint humano.",
        allowed="Skill Read Glob Grep", max_turns=15,
    )
    runs["no-auto-workflow"] = r
    workflow_skills = {f"scrumaidev-{w}" for w in WORKFLOWS}
    attempts = [a for a in skill_attempts(r) if a["skill"].split(":")[-1] in workflow_skills]
    accepted = [a for a in attempts
                if not (a["result"].get("is_error") and "disable-model-invocation" in a["result"].get("content", ""))]
    check(checks, "C5", "workflow skills cannot be model-invoked (attempts refused by the harness)",
          not accepted,
          {"workflow_skill_attempts": attempts, "accepted": accepted, "reads": read_paths(r),
           "final_text_excerpt": r["result_text"][:800]})

    # C6: main-loop model is stable across every run.
    per_run = {k: v["assistant_models"] for k, v in runs.items()}
    init_models = {k: v["init"].get("model") for k, v in runs.items()}
    main_models = {m for models in per_run.values() for m in models}
    check(checks, "C6", "main-loop model unchanged while ScrumAIDev skills run",
          len(set(init_models.values())) == 1 and main_models <= set(init_models.values()),
          {"init_model": init_models, "assistant_models": per_run,
           "note": "modelUsage may also list a small background model used by the harness itself",
           "model_usage": {k: v["model_usage"] for k, v in runs.items()}})

    # C7: commit attribution rule.
    r = claude.ask(
        green,
        "Escreva a mensagem de commit completa que voce usaria para adicionar docs/hello.md neste "
        "repositorio, seguindo as regras do projeto. Responda apenas com a mensagem. Nao execute git.",
        allowed="Read Glob Grep", disallowed="Bash Write Edit", max_turns=10,
    )
    runs["commit-message"] = r
    check(checks, "C7", "proposed commit message has no AI Co-authored-by trailer",
          r["result_subtype"] == "success" and bool(r["result_text"].strip())
          and "co-authored-by" not in r["result_text"].lower(),
          {"result_subtype": r["result_subtype"], "message": r["result_text"][:800]})

    passed = sum(c["status"] == "PASS" for c in checks)
    report = {
        "versions": versions,
        "model": sorted(set(init_models.values())),
        "workdir": str(root),
        "summary": f"{passed}/{len(checks)} PASS",
        "total_cost_usd": round(claude.cost, 4),
        "checks": checks,
    }
    out = root / "live_validation_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, r in runs.items():
        (root / f"run-{name}.jsonl").write_text(r["raw"], encoding="utf-8")
    print(f"\n{report['summary']}  (cost ~ ${report['total_cost_usd']})\nReport: {out}")
    if not args.keep:
        for project in (green, brown):
            shutil.rmtree(project, ignore_errors=True)
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
