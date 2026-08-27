#!/usr/bin/env bash
# Deploys the already-pulled checkout on the server.
# Invoked by the GitHub Actions deploy job as:
#   cd ~/clients/Nexchemical && git pull --ff-only && bash scripts/deploy.sh
# Wrapped in main() so a mid-run `git pull` updating this file can't
# corrupt the executing script.
set -euo pipefail

main() {
    cd "$(dirname "$0")/../nexchemicalBack"

    # One-time migration: this app directory was renamed from principalBack/
    # to nexchemicalBack/ in 0563d28 (2026-08-26). Git replays renames for
    # tracked files, but venv/, .env, media/, db.sqlite3, and logs/ are
    # gitignored, so they were left behind under the old directory and broke
    # the first deploy after the rename. Sweep them over once; every deploy
    # after that is a no-op here since the items already exist.
    LEGACY_DIR="$(pwd)/../principalBack"
    if [ -d "$LEGACY_DIR" ]; then
        for item in venv .env media db.sqlite3 logs; do
            if [ ! -e "$item" ] && [ -e "$LEGACY_DIR/$item" ]; then
                echo "Migrating $item from principalBack/ (one-time folder-rename fixup)"
                mv "$LEGACY_DIR/$item" "$item"
            fi
        done
    fi

    if [ ! -x ./venv/bin/pip ]; then
        echo "ERROR: ./venv not found (or has no pip). Create it first:" >&2
        echo "  python3 -m venv venv && ./venv/bin/pip install -r requirements.txt" >&2
        exit 1
    fi

    mkdir -p logs

    ./venv/bin/pip install -q -r requirements.txt
    ./venv/bin/python manage.py migrate --noinput
    ./venv/bin/python manage.py collectstatic --noinput >/dev/null
    ./venv/bin/python manage.py check --deploy --fail-level ERROR

    PIDFILE=gunicorn.pid
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        # Graceful reload: gunicorn re-imports the app, no dropped requests.
        kill -HUP "$(cat "$PIDFILE")"
        echo "gunicorn reloaded (pid $(cat "$PIDFILE"))"
    else
        ./venv/bin/gunicorn config.wsgi:application \
            --bind 0.0.0.0:5000 --workers 3 \
            --daemon --pid "$PIDFILE" \
            --access-logfile logs/access.log --error-logfile logs/error.log
        echo "gunicorn started (pid $(cat "$PIDFILE"))"
    fi

    sleep 2
    curl -sf -o /dev/null http://127.0.0.1:5000/ && echo "healthcheck OK"
}

main "$@"
