# Desktop File Organizer

![Python CI](https://github.com/vincentokello770-arch/desktop-file-organizer/actions/workflows/python-ci.yml/badge.svg?branch=main)

A Python command-line utility that organizes files in a selected directory
into extension-based categories. Built as a practical software engineering
portfolio project, with safety controls and automated tests.

## Business Problem

Desktop and shared working folders can accumulate documents, spreadsheets,
images, source code, archives, and other files. Finding items becomes slower
when files are not organized consistently.

This tool automates basic file classification and movement while allowing
the user to preview proposed changes before applying them.

## Features

- Preview mode by default; files are not moved unless `--apply` is supplied.
- Categorizes common documents, spreadsheets, images, videos, audio,
  archives, code files, installers, and unknown file types.
- Avoids overwriting an existing destination filename by choosing a
  numbered alternative.
- Processes only files directly inside the selected directory.
- Skips subdirectories, symbolic links, Windows shortcuts, and selected
  protected system filenames.
- Reports moved, previewed, skipped, and failed items.
- Writes activity and error details to a local log file.
- Uses Python's standard library for runtime functionality.
- Includes automated tests using temporary directories.

## Technology Stack

- Python
- pathlib and shutil for filesystem operations
- argparse for command-line arguments
- logging for diagnostics
- unittest for automated testing
- PowerShell for the Windows development workflow
- Git and GitHub for version control and portfolio presentation

## Requirements

- Python 3.10 or newer
- Windows, macOS, or Linux may work, but the default Desktop discovery and
  logging path are currently designed primarily for Windows.
- No third-party Python packages are required.

## Project Structure

```text
desktop-file-organizer/
├── docs/
│   ├── design-decisions.md
│   └── test-results.md
├── src/
│   └── desktop_file_organizer/
│       ├── __init__.py
│       └── organizer.py
├── tests/
│   └── test_organizer.py
├── .gitignore
└── README.md
```

## Setup

Clone the repository, then open PowerShell in the project directory.

```powershell
$env:PYTHONPATH = Join-Path (Get-Location).Path "src"
```

No dependency installation is required.

## Usage

### 1. Preview a chosen directory

```powershell
python -m desktop_file_organizer.organizer --directory "C:\Path\To\Folder"
```

Preview is the default. It displays planned destinations without moving files.

### 2. Apply the organization

```powershell
python -m desktop_file_organizer.organizer --directory "C:\Path\To\Folder" --apply
```

Use `--apply` only after reviewing the preview and confirming the target path.

### 3. Use the detected Windows Desktop

```powershell
python -m desktop_file_organizer.organizer
```

This attempts to find a conventional Desktop directory. If your Desktop is
redirected to a location that the application does not detect, use
`--directory` to specify it explicitly.

### 4. Run automated tests

From the repository root:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location).Path "src"
python -m unittest discover -s tests -v
```

### 5. Display command-line options

```powershell
python -m desktop_file_organizer.organizer --help
```

## Verification Evidence

The initial automated test suite passed.

A separate end-to-end demonstration used five generated sample files:

| Measure | Observed result |
|---|---:|
| Files previewed | 5 |
| Files moved in preview mode | 0 |
| Files moved in apply mode | 5 |
| Errors during apply | 0 |
| Existing directories skipped | 1 |
| Expected file paths verified | 6 |
| Sample file contents verified | 5 |

The six verified paths included five organized files and one file preserved
inside an existing subdirectory. The five sample file contents were also
checked after the moves.

See [the test results](docs/test-results.md) for the test scope and
limitations.

## Security and Reliability Considerations

- Preview-first behavior reduces accidental movement.
- The tool does not recursively reorganize subdirectories.
- Filename collision handling reduces the risk of overwriting existing files.
- The program does not upload files or require cloud services.
- Automated tests use temporary directories rather than the user's real
  Desktop.
- File movement is not transactional. An interruption can leave some files
  moved and others unmoved.
- Filename checks cannot eliminate every race condition if another process
  changes the destination concurrently.
- This application is not a backup or rollback system. Back up important
  data before applying changes to valuable directories.
- The program classifies by extension; it does not inspect file contents
  to verify the actual file type.

## Cost

The application has no cloud runtime costs and requires no third-party
Python packages. Development and Git hosting costs depend on the tools
and services chosen by the user.

## Current Limitations

- No graphical user interface.
- No undo or automated rollback.
- No recursive organization.
- No configurable category rules.
- No dry-run report export.
- No performance benchmark on large directories.
- Cross-platform behavior has not been fully tested.

## Roadmap

- Add tests for protected filenames, shortcuts, symbolic links, and error cases.
- Improve collision handling and file-movement reliability.
- Add structured reports and a summary suitable for business users.
- Add continuous integration with GitHub Actions.
- Measure performance using reproducible test data.
- Improve packaging and command-line installation.

## License

No license has been selected yet. Until one is added, do not assume others
have permission to redistribute or reuse this project.

