# File Integrity Lab

A small offline Python tool that records SHA-256 hashes and reports added, removed, and modified files. It is designed to practice content hashing, baseline comparison, and investigation of unexpected changes.

## Run the demo

Requires Python 3.12+ for Windows junction checks; Python 3.10+ is supported for ordinary directories on Linux/macOS. Standard library only. From the repository directory:

```sh
python integrity.py baseline demo-files baseline.json
python integrity.py check demo-files baseline.json
python -m unittest discover -s tests -v
```

Use `python3` if necessary. The first command writes a new manifest outside the monitored folder. It refuses to overwrite an existing manifest; choose another filename when creating another baseline. The second prints empty change lists for the unchanged demo. Edit `demo-files/settings.txt` and run check again to see it in `modified`.

Exit codes: 0 = baseline created or no changes; 1 = check found changes; 2 = input, filesystem, or validation error. No network access, credentials, administrator privileges, or third-party packages are needed. The tool does not restore, delete, or quarantine monitored files.

## How it works

Files are hashed in 64 KiB blocks. Paths in the manifest are relative to the monitored directory and use forward slashes. Comparisons use path and file content, not size or modification time. A rename appears as removal plus addition. Empty directories, metadata, ownership, ACLs, alternate data streams, and executable permissions are not monitored.

Store the baseline outside the monitored directory to avoid hashing the manifest itself. Treat it as trusted evidence: an attacker who can change both baseline and files can hide modifications. This tool does not sign manifests or establish their authenticity. Manifest paths are validated and only compared as strings; they are never used to open files during comparison.

## Filesystem limits

Do not run this as a privileged process or against hostile, actively changing trees. Links/junctions are rejected when encountered, but traversal and file opening are not race-proof; a concurrent replacement can defeat those checks. Windows junction detection needs Python 3.12+. A snapshot is not atomic, so a changing file can yield inconsistent results. Use a quiet test directory and trusted ordinary files. Hard links are treated as files, not rejected.

The tool reads monitored content and emits filenames and hashes, so keep real manifests private. There is no scheduling, live monitoring, malware classification, or production hardening. See `docs/investigation.md` for interpretation and exercises.

## Provenance and verification

Educational project using harmless invented demo files. No real compromise, production deployment, or security efficacy is claimed. Tests cover a known SHA-256 vector, binary files, same-size content changes, validation, classifications, exit codes, and overwrite prevention. CI targets Windows and Linux on Python 3.10/3.12, but Python 3.10 Windows runs test only ordinary directories. MIT licensed.
