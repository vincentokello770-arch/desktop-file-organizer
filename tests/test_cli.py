"""Integration tests for the Desktop File Organizer command-line interface."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"


class CliIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

        self.environment = os.environ.copy()
        existing_pythonpath = self.environment.get("PYTHONPATH", "")
        paths = [str(SOURCE_DIRECTORY)]

        if existing_pythonpath:
            paths.append(existing_pythonpath)

        self.environment["PYTHONPATH"] = os.pathsep.join(paths)

        (self.root / "sample.txt").write_text(
            "Test document",
            encoding="utf-8",
        )
        (self.root / "sales.csv").write_text(
            "item,amount\nPen,100",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_cli(self, *arguments):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "desktop_file_organizer.organizer",
                "--directory",
                str(self.root),
                *arguments,
            ],
            cwd=PROJECT_ROOT,
            env=self.environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def test_cli_preview_preserves_files_and_creates_no_category_folders(self):
        result = self.run_cli()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Mode: PREVIEW", result.stdout)
        self.assertIn("Files previewed: 2", result.stdout)
        self.assertIn("Files moved:     0", result.stdout)
        self.assertIn("Errors:          0", result.stdout)

        self.assertTrue((self.root / "sample.txt").is_file())
        self.assertTrue((self.root / "sales.csv").is_file())
        self.assertFalse((self.root / "Documents").exists())
        self.assertFalse((self.root / "Spreadsheets").exists())

    def test_cli_missing_directory_returns_error_without_traceback(self):
        missing_directory = self.root / "directory-that-does-not-exist"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "desktop_file_organizer.organizer",
                "--directory",
                str(missing_directory),
            ],
            cwd=PROJECT_ROOT,
            env=self.environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR:", result.stdout)
        self.assertIn("Directory does not exist", result.stdout)
        self.assertNotIn("Traceback (most recent call last)", result.stderr)
        self.assertFalse(missing_directory.exists())

    def test_cli_apply_moves_files_and_reports_success(self):
        result = self.run_cli("--apply")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Mode: APPLY", result.stdout)
        self.assertIn("Files moved:     2", result.stdout)
        self.assertIn("Errors:          0", result.stdout)

        self.assertTrue((self.root / "Documents" / "sample.txt").is_file())
        self.assertTrue(
            (self.root / "Spreadsheets" / "sales.csv").is_file()
        )
        self.assertFalse((self.root / "sample.txt").exists())
        self.assertFalse((self.root / "sales.csv").exists())


if __name__ == "__main__":
    unittest.main()
