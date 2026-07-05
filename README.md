# personal-automation

Homelab-only automation jobs, split out of the `dotfiles` repo (2026-07).
Dotfiles keeps everything every device needs (config deploy/pull, repo
pulling, shared utils); this repo holds the jobs that only run on homelab
machines:

| Path | Purpose |
|------|---------|
| `src/bitwarden.py` | Bitwarden vault backup (json + csv exports, per user and per org). Runs in the `Dockerfile-bitwarden_backup` container. |
| `src/utils/` | **Vendored from dotfiles** `src/utils/` — see below. |
| `src/config.py` | Trimmed copy of dotfiles `src/config.py` (path variables + data dir creation). |

This repo is **local and unpublished**. Jason decides if/when it gets a
remote; if pushed, default to a **private** repo (it orbits credentialed
services). No secrets are committed — see `.env` below.

## Vendored `src/utils/` modules

Copied from dotfiles `src/utils/` so the moved jobs' imports are unchanged
(`from utils.x import y`). Dotfiles keeps its own copies (other dotfiles
scripts still use them); if you touch one here, consider syncing the change.

| Module | Status |
|--------|--------|
| `config_utils.py` | verbatim copy |
| `display_tools.py` | verbatim copy |
| `host_tools.py` | verbatim copy |
| `json_tools.py` | verbatim copy |
| `date_tools.py` | **trimmed**: only `get_datetime_format_string` / `get_current_datetime` (all `bitwarden.py` uses). The full module builds week/day lookup tables from committed CSVs at import time and raises `KeyError` once today's date is past the CSVs — a bad failure mode for an unattended backup job, so the tables were deliberately not vendored. |

## Setup

Uses [uv](https://docs.astral.sh/uv/) (Python version pinned in
`.python-version`):

```bash
uv sync
```

### `.env` (secrets — never committed)

Same pattern as dotfiles: `.env` is a symlink into the credentials repo,
which is cloned next to this repo:

```bash
ln -s ../personal_credentials/personal.env .env
```

Variables used here: `BITWARDEN_URL`, `BITWARDEN_ORG_CONFIGS`,
`BITWARDEN_USERNAME`/`BITWARDEN_PASSWORD` (+ `_SECONDARY` pair),
`PERSONAL_CREDENTIALS_DIR` (optional override), `LOG_LEVEL` (optional).

## Bitwarden backup — Docker

Two-step process: **build the image first, then run it.** Run both commands
from the repo root (where `.env` and `Dockerfile-bitwarden_backup` live).

At run time the container loads config (`BITWARDEN_URL`,
`BITWARDEN_ORG_CONFIGS`, credentials, etc.) from your `.env`. The `.env` is
**mounted** into the container rather than baked into the image or passed with
`--env-file` — the script's `.env` loader strips the surrounding quotes that
most of these values use, whereas `docker --env-file` would pass them through
literally (e.g. `LOG_LEVEL="info"` → `"info"`) and break.

### Linux / macOS

1. Build the image:

```bash
docker build -t personal-automation-bitwarden_backup \
  --build-arg HOSTNAME=$(hostname) \
  --build-arg BITWARDEN_URL=$(grep '^BITWARDEN_URL=' .env | cut -d '=' -f2- | tr -d '"') \
  -f Dockerfile-bitwarden_backup .
```

1. Run it (mount `.env` read-only, the data volume, and the
   `personal_credentials` folder):

```bash
docker run \
  -v "$(pwd)/.env:/personal-automation/.env:ro" \
  -v "$(pwd)/data:/personal-automation/data" \
  -v "$(pwd)/../personal_credentials:/personal_credentials" \
  personal-automation-bitwarden_backup
```

The JSON exports are also copied to `personal_credentials/bitwarden_exports`.
The image sets `PERSONAL_CREDENTIALS_DIR=/personal_credentials`, so the third
mount maps that back to `../personal_credentials` on the host — matching where
a non-Docker run would put it (`~/GitHub/personal_credentials`). To use a
different location, override the env var (`-e PERSONAL_CREDENTIALS_DIR=...`)
and mount accordingly.

### Windows (PowerShell)

1. Build the image:

   ```powershell
   $bitwardenUrl = (Get-Content .env | Where-Object { $_ -match "^BITWARDEN_URL=" }) -replace 'BITWARDEN_URL=', '' -replace '"', ''

   docker build -t personal-automation-bitwarden_backup `
     --build-arg HOSTNAME=$(hostname) `
     --build-arg BITWARDEN_URL=$bitwardenUrl `
     -f Dockerfile-bitwarden_backup .
   ```

2. Run it (mount `.env` read-only and the data volume):

   ```powershell
   docker run `
     -v "${PWD}/.env:/personal-automation/.env:ro" `
     -v "${PWD}/data:/personal-automation/data" `
     -v "${PWD}/../personal_credentials:/personal_credentials" `
     personal-automation-bitwarden_backup
   ```

## Bitwarden Manual Backup - CLI

```bash
# {"object":"organization","id":{{ ORG_ID }},"name":"CrownCentral","status":2,"type":1,"enabled":true}
bw config server {{ BITWARDEN_URL }}

bw login
# enter username and password

bw sync

bw export --output "/My_Backup/data/bitwarden_backup_$(echo $HOSTNAME | tr '[:upper:]' '[:lower:]').json" --format json
# enter password

bw export --output /My_Backup/data/bitwarden_backup_$(echo $HOSTNAME | tr '[:upper:]' '[:lower:]').csv --format csv
# enter password

bw list organizations
# enter password

bw export --organizationid {{ ORG_ID }} --output "/My_Backup/data/bitwarden_backup_$(echo $HOSTNAME | tr '[:upper:]' '[:lower:]')_CrownCentral.json" --format json
# enter password

bw export --organizationid {{ ORG_ID }} --output "/My_Backup/data/bitwarden_backup_$(echo $HOSTNAME | tr '[:upper:]' '[:lower:]')_CrownCentral.csv" --format csv
# enter password
```

## Lint

```bash
uv run flake8 .   # max-line-length 120, max-complexity 15
uv run isort .    # black profile
```

## Cutover checklist (Jason executes — nothing here happens automatically)

Full consumer audit of dotfiles done 2026-07-05: **no crontab on any host
references either script** (checked all `triggers/crontab_extraction_*.txt`:
behemoth, elitedesk, elitedesk_root, hellofreshjason, macmini14, nukbuntu,
raspberrypi0/3/3a/4/4a (+roots), tower), and `docs/homelab_deployments.md` /
`ansible_playbooks/` / `scripts/` / shell aliases reference neither. The only
consumer was **manual, per the dotfiles README**: the Docker build/run for
the Bitwarden backup.

Per host that runs the Bitwarden backup (known from existing exports: `envy`;
plus any other machine you have built `dotfiles-bitwarden_backup` on —
check with `docker images | grep bitwarden`):

1. [ ] Get this repo onto the host at `~/GitHub/personal-automation`
       (it is local-only until you publish it — copy it over, or push it to a
       **private** remote first; your call).
2. [ ] `ln -s ../personal_credentials/personal.env .env` in the repo root.
3. [ ] Rebuild the image from this repo with the new tag
       (`personal-automation-bitwarden_backup`) — commands above.
4. [ ] Run it once and confirm exports land in `data/` and
       `personal_credentials/bitwarden_exports/`.
5. [ ] Remove the old image: `docker rmi dotfiles-bitwarden_backup`.
6. [ ] Optional: move old exports out of `dotfiles/data/`
       (`bitwarden_backup_*.json|csv` and `data/archive/`) into this repo's
       `data/` so history lives in one place (both `data/` dirs are
       gitignored).

Dotfiles side (already done in the `repo-improvements` branch, listed for
awareness):

- `src/bitwarden.py`, `src/parse_minecraft_logs.py`,
  `Dockerfile-bitwarden_backup`, `.dockerignore` removed; README's Docker /
  `bw export` sections replaced with a pointer here; `matplotlib` dropped
  from `pyproject.toml`.
- `src/utils/` (including `json_tools.py`, whose normalizer the backup uses)
  **stays in dotfiles** — this repo vendors its own copies.

Retired: `parse_minecraft_logs.py` (moved here 2026-07-05, deleted the same
day — no longer needed). Its exclusive deps (`matplotlib`, `paramiko`, `scp`)
and `.env` variables (`UNRAID_*`, `MINECRAFT_SERVER_USER_CONFIGS`) were
removed with it; recover from git history if ever wanted.
