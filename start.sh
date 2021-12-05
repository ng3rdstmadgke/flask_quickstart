#!/bin/bash

SCRIPT_DIR="$(cd $(dirname $0); pwd)"
cd "$SCRIPT_DIR"

# hello.pyにアプリケーションがある場合の記述
uwsgi --http 127.0.0.1:5000 --module hello:app
