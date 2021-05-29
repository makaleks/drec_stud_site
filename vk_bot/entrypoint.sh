#!/bin/bash
PYTHONPATH=/app/:$PYTHONPATH
export PYTHONPATH;
cd /app/src/ || exit 0
python bot.py