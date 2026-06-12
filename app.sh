#!/bin/bash
exec gunicorn app:app --bind 0.0.0.0:8080 --workers 1 --timeout 300
