#!/usr/bin/env python3
"""Unit tests for agileaidev_gate.py.

Run with: python -m unittest scripts.test_agileaidev_gate -v
(from the repository root)
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import agileaidev_gate as gate  # noqa: E402


class TempRootTestCase(unittest.TestCase):
    """Base class that points gate.ROOT at a throwaway directory."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._original_root = gate.ROOT
        gate.ROOT = self.root

    def tearDown(self) -> None:
        gate.ROOT = self._original_root
        self._tmp.cleanup()


class ReadPackageScriptsTests(unittest.TestCase):
    def test_returns_script_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package_json = Path(tmp) / "package.json"
            package_json.write_text(json.dumps({"scripts": {"lint": "eslint .", "test": "vitest"}}))
            self.assertEqual(gate.read_package_scripts(package_json), {"lint", "test"})

    def test_missing_scripts_key_returns_empty_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package_json = Path(tmp) / "package.json"
            package_json.write_text(json.dumps({"name": "demo"}))
            self.assertEqual(gate.read_package_scripts(package_json), set())

    def test_scripts_not_a_dict_returns_empty_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package_json = Path(tmp) / "package.json"
            package_json.write_text(json.dumps({"scripts": ["lint"]}))
            self.assertEqual(gate.read_package_scripts(package_json), set())

    def test_invalid_json_returns_empty_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package_json = Path(tmp) / "package.json"
            package_json.write_text("{not valid json")
            self.assertEqual(gate.read_package_scripts(package_json), set())

    def test_missing_file_returns_empty_set(self) -> None:
        missing = Path("does") / "not" / "exist.json"
        self.assertEqual(gate.read_package_scripts(missing), set())


class FrontendRunnerTests(unittest.TestCase):
    def test_prefers_pnpm_when_lockfile_and_binary_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            frontend = Path(tmp)
            (frontend / "pnpm-lock.yaml").touch()
            with mock.patch.object(gate.shutil, "which", return_value="/usr/bin/pnpm"):
                self.assertEqual(gate.frontend_runner(frontend), ["pnpm", "--dir", str(frontend)])

    def test_falls_back_to_yarn_when_pnpm_binary_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            frontend = Path(tmp)
            (frontend / "pnpm-lock.yaml").touch()
            (frontend / "yarn.lock").touch()
            with mock.patch.object(gate.shutil, "which", side_effect=lambda cmd: "/usr/bin/yarn" if cmd == "yarn" else None):
                self.assertEqual(gate.frontend_runner(frontend), ["yarn", "--cwd", str(frontend)])

    def test_defaults_to_npm_without_lockfiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            frontend = Path(tmp)
            with mock.patch.object(gate.shutil, "which", return_value=None):
                self.assertEqual(gate.frontend_runner(frontend), ["npm", "--prefix", str(frontend)])


class MakeHasTargetTests(unittest.TestCase):
    def test_missing_makefile_returns_false(self) -> None:
        self.assertFalse(gate.make_has_target(Path("no") / "such" / "Makefile", "lint"))

    def test_detects_declared_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            makefile = Path(tmp) / "Makefile"
            makefile.write_text("lint:\n\techo lint\n")
            self.assertTrue(gate.make_has_target(makefile, "lint"))

    def test_missing_target_returns_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            makefile = Path(tmp) / "Makefile"
            makefile.write_text("lint:\n\techo lint\n")
            self.assertFalse(gate.make_has_target(makefile, "test"))


class RunStandardGateTests(TempRootTestCase):
    def test_no_stack_detected_returns_zero(self) -> None:
        self.assertEqual(gate.run_standard_gate("lint"), 0)

    def test_delegates_to_frontend_script_when_present(self) -> None:
        frontend = self.root / "frontend"
        frontend.mkdir()
        (frontend / "package.json").write_text(json.dumps({"scripts": {"lint": "eslint ."}}))

        with mock.patch.object(gate, "run", return_value=0) as run_mock:
            self.assertEqual(gate.run_standard_gate("lint"), 0)
        run_mock.assert_called_once_with(["npm", "--prefix", str(frontend), "run", "lint"])

    def test_frontend_present_without_script_still_returns_zero(self) -> None:
        frontend = self.root / "frontend"
        frontend.mkdir()
        (frontend / "package.json").write_text(json.dumps({"scripts": {"build": "vite build"}}))

        self.assertEqual(gate.run_standard_gate("lint"), 0)

    def test_delegates_to_backend_makefile_when_present(self) -> None:
        backend = self.root / "backend"
        backend.mkdir()
        (backend / "Makefile").write_text("test:\n\tpytest\n")

        with mock.patch.object(gate, "run", return_value=0) as run_mock:
            self.assertEqual(gate.run_standard_gate("test"), 0)
        run_mock.assert_called_once_with(["make", "-C", "backend", "test"])


class ValidateContractTests(TempRootTestCase):
    def test_no_contracts_returns_zero(self) -> None:
        self.assertEqual(gate.validate_contract(), 0)

    def test_contracts_without_validator_returns_zero(self) -> None:
        contracts = self.root / "docs" / "contracts"
        contracts.mkdir(parents=True)
        (contracts / "api.yaml").write_text("openapi: 3.0.0\n")

        with mock.patch.object(gate.shutil, "which", return_value=None):
            self.assertEqual(gate.validate_contract(), 0)

    def test_contracts_with_spectral_delegates(self) -> None:
        contracts = self.root / "docs" / "contracts"
        contracts.mkdir(parents=True)
        contract_file = contracts / "api.yaml"
        contract_file.write_text("openapi: 3.0.0\n")

        with mock.patch.object(gate.shutil, "which", side_effect=lambda cmd: "/usr/bin/spectral" if cmd == "spectral" else None):
            with mock.patch.object(gate, "run", return_value=0) as run_mock:
                self.assertEqual(gate.validate_contract(), 0)
        run_mock.assert_called_once_with(["spectral", "lint", str(contract_file)])


class MainDispatchTests(TempRootTestCase):
    def test_unknown_gate_returns_two(self) -> None:
        self.assertEqual(gate.main(["not-a-real-gate"]), 2)

    def test_empty_argv_runs_default_gates_on_empty_project(self) -> None:
        self.assertEqual(gate.main([]), 0)

    def test_stops_on_first_failure(self) -> None:
        calls = []

        def fake_handler(g: str) -> int:
            calls.append(g)
            return 1

        with mock.patch.dict(gate.GATES, {"lint": fake_handler, "test": fake_handler}):
            self.assertEqual(gate.main(["lint", "test"]), 1)
        self.assertEqual(calls, ["lint"])


if __name__ == "__main__":
    unittest.main()
