#!/bin/bash

# === Configuration ===
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$PROJECT_DIR/data"
ENV_FILE="$DATA_DIR/.env"
CONFIG_FILE="$PROJECT_DIR/cfg.ini"
VENV_DIR="$PROJECT_DIR/venv"
APP_FILE="$PROJECT_DIR/app.py"

# === Ensure Python venv exists ===
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Python virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install -r "$PROJECT_DIR/requirements.txt"
else
    source "$VENV_DIR/bin/activate"
fi

# === Ensure data directory exists ===
mkdir -p "$DATA_DIR"

# === Info to user ===
echo "✅ Launching app..."
echo " - .env path: $ENV_FILE"
echo " - cfg.ini path: $CONFIG_FILE"

# === Start the app ===
export ENV_PATH="$ENV_FILE"
python "$APP_FILE"