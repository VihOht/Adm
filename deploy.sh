#!/usr/bin/env bash
set -Eeuo pipefail
export PATH="$HOME/.local/bin:$PATH"
unset PYTHONHOME PYTHONPATH || true

APP_DIR="/home/ec2-user/Adm"
VENV="$APP_DIR/.venv"
PYVER="3.13"

cd "$APP_DIR"
uv python install "$PYVER"
uv venv --python "$PYVER" "$VENV"

if [[ -f "pyproject.toml" ]]; then
  uv sync --no-dev --python "$VENV/bin/python"
elif [[ -f "requirements.txt" ]]; then
  uv pip install --python "$VENV/bin/python" -r requirements.txt
fi

"$VENV/bin/python" manage.py migrate --noinput
"$VENV/bin/python" manage.py collectstatic --noinput
sudo systemctl restart gunicorn
sudo systemctl reload nginx
echo "Deploy complete ✅"
