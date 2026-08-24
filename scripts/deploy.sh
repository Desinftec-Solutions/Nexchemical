#!/usr/bin/env bash
# Deploys the already-pulled checkout on the server.
# Invoked by the GitHub Actions deploy job as:
#   cd ~/clients/Nexchemical && git pull --ff-only && bash scripts/deploy.sh
# Wrapped in main() so a mid-run `git pull` updating this file can't
# corrupt the executing script.
set -euo pipefail

main() {
    cd "$(dirname "$0")/../principalBack"

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
