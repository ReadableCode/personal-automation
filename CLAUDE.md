# CLAUDE.md

Guidance for Claude Code (and other AI agents) working in this repository.

## What this repo is

**Homelab-only automation jobs**, split out of the `dotfiles` repo (2026-07).
Dotfiles keeps everything a device Jason touches needs (config deploy/pull,
repo pulling, shared utils); this repo holds the jobs that only ever run on
homelab machines:

- `src/bitwarden.py` — Bitwarden vault backup (runs via the
  `Dockerfile-bitwarden_backup` container; exports land in `data/` and are
  copied into the `personal_credentials` repo).
- `src/parse_minecraft_logs.py` — pulls/streams Minecraft server logs from the
  unRAID box over SSH; interactive analysis via the `# %%` code cells.

`src/utils/` is **vendored from dotfiles** `src/utils/` (see README); keep the
package name `utils` so imports stay identical to dotfiles.

## Python environment & tooling

Uses **uv** (Python 3.10, pinned in `.python-version`):

```bash
uv sync                      # install deps from pyproject.toml / uv.lock
uv run python src/<script>.py
```

Lint / format / type-check (config in `.flake8`, `.isort.cfg`,
`pyproject.toml` — same rules as dotfiles):

```bash
uv run flake8 .              # max-line-length 120, max-complexity 15
uv run isort .               # black profile
uv run mypy .                # ignore_missing_imports = true
```

## Conventions

- **No secrets in the repo.** `.env` is a symlink to
  `../personal_credentials/personal.env` and is gitignored — keep it that way;
  never inline credential values.
- This repo is **local/unpublished** until Jason decides otherwise; if it is
  ever pushed, it defaults to a private remote (it orbits credentialed
  services). Do not create remotes or push without being asked.
- Match nearby code style; run isort before committing; respect flake8's
  120-char lines.
- Vendored `src/utils/` modules: prefer keeping them byte-identical to their
  dotfiles counterparts (except the documented `date_tools.py` trim) so they
  are easy to re-sync.
