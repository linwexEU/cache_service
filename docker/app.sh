#!/bin/bash

cd src/

uv run alembic upgrade head 

cd ..

uv run gunicorn src.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000