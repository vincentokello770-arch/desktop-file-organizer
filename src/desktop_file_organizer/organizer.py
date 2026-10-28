"""Safe, non-recursive file organization for a selected directory."""

import argparse
import logging
import os
import shutil
from pathlib import Path


CATEGORIES = {
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
        ".ppt", ".pptx", ".odp",
    },
    "Spreadsheets": {
        ".xls", ".xlsx", ".csv", ".ods",
    },
    "Images": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
        ".svg", ".tiff", ".ico",
    },
    "Videos": {
        ".mp4", ".mkv", ".mov", ".avi", ".wmv", ".webm",
        ".flv", ".mpeg", ".mpg",
    },
    "Audio": {
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a",
        ".wma",
    },
    "Archives": {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2",
    },
    "Code": {
        ".py", ".js", ".ts", ".html", ".css", ".json",
        ".xml", ".yaml", ".yml", ".sql", ".sh", ".ps1",
        ".java", ".cpp", ".c", ".cs", ".php", ".r",
        ".ipynb",
    },
    "Installers": {
        ".exe", ".msi", ".msix", ".appx",
    },
}

PROTECTED_NAMES = {"desktop.ini", "thumbs.db"}
LOGGER = logging.getLogger("desktop_file_organizer")


def classify_file(file_path):
    """Return the category associated with a file extension."""
    extension = Path(file_path).suffix.lower()

    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category

    return "Other"


def unique_destination(destination):
    """Return a destination that will not overwrite an existing file."""
    destination = Path(destination)

    if not destination.exists():
        return destination

    counter = 1

    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1


def organize_directory(directory, apply_changes=False):
    """
    Preview or organize files directly inside directory.

    Returns counts and a list of planned, completed, skipped, or failed
    actions. Existing directories are never recursively reorganized.
    """
    directory = Path(directory).expanduser().resolve()

    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    result = {
        "previewed": 0,
        "moved": 0,
        "skipped": 0,
        "errors": 0,
        "actions": [],
    }

    # Snapshot the immediate directory contents to avoid processing
    # newly created category folders during this run.
    for item in list(directory.iterdir()):
        try:
            if item.is_symlink() or not item.is_file():
                result["skipped"] += 1
                result["actions"].append(
                    ("SKIPPED", item.name, "not a regular file")
                )
                continue

            if item.name.lower() in PROTECTED_NAMES:
                result["skipped"] += 1
                result["actions"].append(
                    ("SKIPPED", item.name, "protected system file")
                )
                continue

            if item.suffix.lower() == ".lnk":
                result["skipped"] += 1
                result["actions"].append(
                    ("SKIPPED", item.name, "Windows shortcut")
                )
                continue

            category = classify_file(item)
            destination_folder = directory / category
            destination = unique_destination(
                destination_folder / item.name
            )

            if not apply_changes:
                result["previewed"] += 1
                result["actions"].append(
                    ("PREVIEW", item.name, str(destination))
                )
                continue

            destination_folder.mkdir(exist_ok=True)

            # Recheck immediately before moving.
            destination = unique_destination(
                destination_folder / item.name
            )

            shutil.move(str(item), str(destination))

            result["moved"] += 1
            result["actions"].append(
                ("MOVED", item.name, str(destination))
            )
            LOGGER.info("Moved %s to %s", item, destination)

        except (OSError, shutil.Error) as error:
            result["errors"] += 1
            result["actions"].append(
                ("ERROR", item.name, str(error))
            )
            LOGGER.exception("Could not process %s", item)

    return result


def find_desktop():
    """Locate a conventional Windows Desktop directory."""
    candidates = []

    one_drive = os.environ.get("OneDrive")
    if one_drive:
        candidates.append(Path(one_drive) / "Desktop")

    candidates.append(Path.home() / "Desktop")

    for candidate in candidates:
        if candidate.is_dir():
            return candidate

    raise FileNotFoundError(
        "Desktop not found. Supply a directory with --directory."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Safely organize files in a directory."
    )
    parser.add_argument(
        "--directory",
        type=Path,
        help="Directory to organize. Defaults to the Windows Desktop.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually move files. Without this option, preview only.",
    )
    args = parser.parse_args()

    try:
        directory = args.directory or find_desktop()

        log_directory = Path.home() / "Documents" / "DesktopOrganizer"
        log_directory.mkdir(parents=True, exist_ok=True)
        log_file = log_directory / "organizer.log"

        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            encoding="utf-8",
        )

        print(f"\nDirectory: {directory.resolve()}")
        print(f"Mode: {'APPLY' if args.apply else 'PREVIEW'}")
        print("-" * 65)

        result = organize_directory(
            directory,
            apply_changes=args.apply,
        )

        for action, filename, detail in result["actions"]:
            print(f"[{action}] {filename} -> {detail}")

        print("-" * 65)
        print(f"Files previewed: {result['previewed']}")
        print(f"Files moved:     {result['moved']}")
        print(f"Items skipped:   {result['skipped']}")
        print(f"Errors:          {result['errors']}")
        print(f"Activity log:    {log_file}")

        if not args.apply:
            print("\nPreview only: no files were moved.")

        if result["errors"]:
            raise SystemExit(1)

    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
