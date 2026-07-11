# Release checklist (control repository)

Use this for Captain's Compass version tags.

1. Ensure the release PR **base is `main`** (not a stack feature branch).
2. `./scripts/doctor.sh` and `./tests/run.sh` pass on `main`.
3. `VERSION` and `CHANGELOG.md` match the release.
4. Merge to `main`.
5. Tag annotated release and push:
   ```bash
   git tag -a vX.Y.Z -m "Captain's Compass vX.Y.Z"
   git push origin vX.Y.Z
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file CHANGELOG.md
   ```
6. Refresh the disposable sandbox:
   ```bash
   ./scripts/update.sh /path/to/captain-compass-sandbox
   ./scripts/doctor.sh /path/to/captain-compass-sandbox
   ```
7. Update `PROGRESS.md`.
