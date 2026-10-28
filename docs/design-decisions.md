# Engineering Design Decisions

## 1. Python Standard Library

Use pathlib and shutil for filesystem operations, argparse for command-line
arguments, logging for diagnostics, and unittest for automated tests.
This avoids third-party runtime dependencies.

## 2. Preview Before Changes

Preview is the default. Moving files requires the explicit --apply flag.

## 3. Avoid Overwriting

If a destination name already exists, choose a numbered alternative such
as report_1.pdf. Tests verify that existing content is preserved.

## 4. Limit the Scan Scope

Only files directly inside the selected directory are processed.
Existing subdirectories are not traversed.

## 5. Test Isolation

Automated tests use temporary directories and generated sample files.
Tests must not depend on, or reorganize, the user's real Desktop.

## 6. Observability

The command-line output summarizes previews, completed moves, skipped
items, and errors. Runtime errors are written to a local log.

## 7. Cost and Dependencies

The application uses Python's standard library and has no cloud costs.

## 8. Known Limitations

The first version is not a backup or rollback system. A process interrupted
during file movement may leave some operations completed. Filename checks
reduce collision risk but do not provide transactional filesystem semantics.
