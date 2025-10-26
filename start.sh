#!/bin/sh
exec gunicorn test_railway_simple:app --bind 0.0.0.0:${PORT:-5000} --timeout 15 --workers 2 --threads 2
