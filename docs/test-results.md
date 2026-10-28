# Test Results and Verification Evidence

## Environment

- Operating system: Windows, using PowerShell
- Python runtime: Python 3.10.6
- Test framework: Python unittest
- Test data: generated files in isolated temporary directories

## Automated Test Results

Latest observed result: **10 tests passed**.

The suite checks:

1. PDF classification.
2. Case-insensitive extension matching.
3. Unknown extension classification.
4. Preview mode without moving files or creating category folders.
5. Moving a file into its category.
6. Preserving an existing destination file during a filename collision.
7. Leaving files inside existing subdirectories untouched.
8. Handling a missing target directory.
9. Skipping the protected `desktop.ini` filename.
10. Skipping Windows `.lnk` shortcuts.

Reproduce the tests from the repository root:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location).Path "src"
python -m unittest discover -s tests -v
```

## End-to-End Demonstration

Five generated sample files were used:

- `report.pdf`
- `sales.csv`
- `photo.JPG`
- `script.py`
- `notes.xyz`

An existing `ExistingFolder\keep.txt` file checked that existing
subdirectories are not recursively processed.

### Preview mode

- Files previewed: 5
- Files moved: 0
- Items skipped: 1
- Errors: 0
- No category folders were created by preview mode.

### Apply mode

- Files moved: 5
- Items skipped: 1
- Errors: 0

### Post-move verification

All six expected file paths existed after organization: five categorized
files and the file retained in the existing subdirectory. The contents
of all five sample files matched their expected values.

## Interpretation and Limitations

These results provide functional evidence for the tested scenarios. They
do not establish production readiness, performance at scale, compatibility
with every filesystem, or guaranteed safety under concurrent filesystem
changes.

Filename collision handling reduces accidental overwrites but does not
eliminate every possible race condition. File movement is not transactional,
and this application does not provide backup or rollback.

## Reproducibility

Results describe the local development session. Re-run the automated tests
after changing the implementation and keep this document aligned with
observed results.
