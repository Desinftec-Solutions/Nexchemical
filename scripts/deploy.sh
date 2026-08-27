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
    # tracked files, but .env, media/, db.sqlite3, and logs/ are gitignored,
    # so they were left behind under the old directory and broke the first
    # deploy after the rename. Sweep them over once; every deploy after that
    # is a no-op here since the items already exist. (venv/ is deliberately
    # NOT swept this way — see below.)
    LEGACY_DIR="$(pwd)/../principalBack"
    if [ -d "$LEGACY_DIR" ]; then
        for item in .env media db.sqlite3 logs; do
            if [ ! -e "$item" ] && [ -e "$LEGACY_DIR/$item" ]; then
                echo "Migrating $item from principalBack/ (one-time folder-rename fixup)"
                mv "$LEGACY_DIR/$item" "$item"
            fi
        done
    fi

    # venv/bin/python(3) is a symlink to the system interpreter, so it keeps
    # working no matter where the venv directory sits — Python resolves its
    # own prefix from pyvenv.cfg next to it, not from a baked-in path. The
    # console-script *wrappers* (pip, gunicorn, ...) are different: each has
    # the venv's absolute path hardcoded in its shebang line, so moving the
    # directory (e.g. the principalBack/ sweep above, or this migration
    # itself, previously) leaves them pointing at a path that no longer
    # exists — pip already broke this way once. Create the venv if it's
    # missing outright; either way, always go through `python -m <tool>`
    # below instead of a wrapper script, since a wrapper isn't guaranteed to
    # get regenerated (pip skips reinstalling an already-satisfied pin).
    if [ ! -e ./venv ]; then
        echo "./venv not found — creating a virtualenv."
        python3 -m venv venv
    fi

    mkdir -p logs

    ./venv/bin/python -m pip install -q -r requirements.txt
    ./venv/bin/python manage.py migrate --noinput
    ./venv/bin/python manage.py collectstatic --noinput >/dev/null
    ./venv/bin/python manage.py check --deploy --fail-level ERROR

    PIDFILE=gunicorn.pid
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        # Graceful reload: gunicorn re-imports the app, no dropped requests.
        kill -HUP "$(cat "$PIDFILE")"
        echo "gunicorn reloaded (pid $(cat "$PIDFILE"))"
    else
        ./venv/bin/python -m gunicorn config.wsgi:application \
            --bind 0.0.0.0:5000 --workers 3 \
            --daemon --pid "$PIDFILE" \
            --access-logfile logs/access.log --error-logfile logs/error.log
        echo "gunicorn started (pid $(cat "$PIDFILE"))"
    fi

    sleep 2
    curl -sf -o /dev/null http://127.0.0.1:5000/ && echo "healthcheck OK"
}

main "$@"
