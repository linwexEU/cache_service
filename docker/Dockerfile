FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

RUN mkdir /micro-cache

WORKDIR /micro-cache

COPY . .

RUN uv sync

RUN chmod a+x /micro-cache/docker/app.sh

CMD ["uv", "run", "gunicorn", "src.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]