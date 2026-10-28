"""Automated tests for the Desktop File Organizer."""

import tempfile
import unittest
from pathlib import Path

from desktop_file_organizer.organizer import (
    classify_file,
    organize_directory,
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

    def test_windows_shortcut_is_skipped(self):
        shortcut = self.root / "important.lnk"
        shortcut.write_text("sample shortcut data", encoding="utf-8")

        result = organize_directory(self.root, apply_changes=True)

        self.assertEqual(result["moved"], 0)
        self.assertEqual(result["skipped"], 1)
        self.assertTrue(shortcut.exists())


if __name__ == "__main__":
    unittest.main()
