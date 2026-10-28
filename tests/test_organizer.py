"""Automated tests for the Desktop File Organizer."""

import tempfile
import unittest
from unittest import mock
from pathlib import Path

from desktop_file_organizer.organizer import (
    classify_file,
    move_without_overwriting,
    organize_directory,
)


class SafeMoveTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_move_helper_moves_file_without_changing_content(self):
        source = self.root / "source.txt"
        destination = self.root / "destination.txt"
        source.write_text("important data", encoding="utf-8")

        returned_path = move_without_overwriting(source, destination)

        self.assertEqual(returned_path, destination)
        self.assertFalse(source.exists())
        self.assertEqual(
            destination.read_text(encoding="utf-8"),
            "important data",
        )

    def test_move_helper_preserves_existing_destination(self):
        source = self.root / "source.txt"
        destination = self.root / "destination.txt"
        source.write_text("new data", encoding="utf-8")
        destination.write_text("original data", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            move_without_overwriting(source, destination)

        self.assertTrue(source.exists())
        self.assertEqual(source.read_text(encoding="utf-8"), "new data")
        self.assertEqual(
            destination.read_text(encoding="utf-8"),
            "original data",
        )

    def test_copy_failure_cleans_up_temporary_file(self):
        source = self.root / "source.txt"
        destination = self.root / "destination.txt"
        source.write_text("important data", encoding="utf-8")

        with mock.patch(
            "desktop_file_organizer.organizer.shutil.copyfileobj",
            side_effect=OSError("simulated copy failure"),
        ):
            with self.assertRaises(OSError):
                move_without_overwriting(source, destination)

        self.assertTrue(source.exists())
        self.assertFalse(destination.exists())
        self.assertEqual(
            list(self.root.glob(".destination.txt.*.tmp")),
            [],
        )


class ClassificationTests(unittest.TestCase):
    def test_pdf_is_document(self):
        self.assertEqual(classify_file(Path("report.pdf")), "Documents")

    def test_extension_matching_is_case_insensitive(self):
        self.assertEqual(classify_file(Path("PHOTO.JPG")), "Images")

    def test_unknown_extension_is_other(self):
        self.assertEqual(classify_file(Path("notes.xyz")), "Other")


class OrganizationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_preview_does_not_move_files_or_create_folders(self):
        source = self.root / "report.pdf"
        source.write_text("sample", encoding="utf-8")

        result = organize_directory(self.root, apply_changes=False)

        self.assertEqual(result["previewed"], 1)
        self.assertEqual(result["moved"], 0)
        self.assertTrue(source.exists())
        self.assertFalse((self.root / "Documents").exists())

    def test_apply_moves_file_into_category(self):
        source = self.root / "photo.jpg"
        source.write_text("sample image", encoding="utf-8")

        result = organize_directory(self.root, apply_changes=True)

        destination = self.root / "Images" / "photo.jpg"

        self.assertEqual(result["moved"], 1)
        self.assertTrue(destination.exists())
        self.assertFalse(source.exists())

    def test_existing_destination_is_not_overwritten(self):
        source = self.root / "report.pdf"
        source.write_text("new content", encoding="utf-8")

        destination_folder = self.root / "Documents"
        destination_folder.mkdir()
        existing = destination_folder / "report.pdf"
        existing.write_text("original content", encoding="utf-8")

        result = organize_directory(self.root, apply_changes=True)

        alternative = destination_folder / "report_1.pdf"

        self.assertEqual(result["moved"], 1)
        self.assertEqual(
            existing.read_text(encoding="utf-8"),
            "original content",
        )
        self.assertEqual(
            alternative.read_text(encoding="utf-8"),
            "new content",
        )

    def test_existing_subdirectory_is_not_processed(self):
        folder = self.root / "MyFolder"
        folder.mkdir()
        nested_file = folder / "report.pdf"
        nested_file.write_text("sample", encoding="utf-8")

        result = organize_directory(self.root, apply_changes=True)

        self.assertTrue(nested_file.exists())
        self.assertEqual(result["moved"], 0)
        self.assertEqual(result["skipped"], 1)

    def test_missing_directory_raises_error(self):
        missing = self.root / "does-not-exist"

        with self.assertRaises(FileNotFoundError):
            organize_directory(missing)

    def test_protected_desktop_ini_is_skipped(self):
        protected_file = self.root / "desktop.ini"
        protected_file.write_text("protected sample", encoding="utf-8")

        result = organize_directory(self.root, apply_changes=True)

        self.assertEqual(result["moved"], 0)
        self.assertEqual(result["skipped"], 1)
        self.assertTrue(protected_file.exists())
        self.assertEqual(
            protected_file.read_text(encoding="utf-8"),
            "protected sample",
        )

    def test_protected_thumbs_db_is_case_insensitive(self):
        protected_file = self.root / "THUMBS.DB"
        protected_file.write_text("protected sample", encoding="utf-8")

        result = organize_directory(self.root, apply_changes=True)

        self.assertEqual(result["moved"], 0)
        self.assertEqual(result["skipped"], 1)
        self.assertTrue(protected_file.exists())
        self.assertEqual(
            protected_file.read_text(encoding="utf-8"),
            "protected sample",
        )

    def test_windows_shortcut_is_skipped(self):
        shortcut = self.root / "important.lnk"
        shortcut.write_text("sample shortcut data", encoding="utf-8")

        result = organize_directory(self.root, apply_changes=True)

        self.assertEqual(result["moved"], 0)
        self.assertEqual(result["skipped"], 1)
        self.assertTrue(shortcut.exists())

    def test_symbolic_link_is_skipped_when_supported(self):
        target_directory = self.root / "targets"
        target_directory.mkdir()
        target = target_directory / "target.pdf"
        target.write_text("target content", encoding="utf-8")
        link = self.root / "linked.pdf"

        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError) as error:
            self.skipTest(
                f"Symbolic link creation unavailable in this environment: {error}"
            )

        result = organize_directory(self.root, apply_changes=True)

        self.assertEqual(result["moved"], 0)
        self.assertGreaterEqual(result["skipped"], 1)
        self.assertTrue(target.exists())
        self.assertTrue(link.is_symlink())
        self.assertEqual(
            target.read_text(encoding="utf-8"),
            "target content",
        )


if __name__ == "__main__":
    unittest.main()
