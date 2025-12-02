FROM python:3.14.0-slim-trixie
RUN groupadd -r appgroup && useradd -r -g appgroup app
WORKDIR /app
RUN pip install pdm
ADD pdm.lock .
ADD pyproject.toml .
ADD src .
ADD README.md .
RUN pdm sync
ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/app/.venv/bin
RUN env-cli --help
USER app
ENTRYPOINT [ "/app/.venv/bin/env-cli" ]