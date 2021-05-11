#!/bin/bash
PYTHONPATH=/app/:$PYTHONPATH
export PYTHONPATH;
cd /app/ || exit 0
python main_service.py
