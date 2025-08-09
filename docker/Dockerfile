FROM ghcr.io/astral-sh/uv:python3.11-alpine

WORKDIR /app

RUN apk update \
    && apk add --no-cache \
    build-base \
    mariadb-dev \
    pkgconfig \
    rust \
    cargo \
    netcat-openbsd \
    && rm -rf /var/cache/apk/*

COPY . .
RUN uv sync --locked

RUN chmod +x /app/bin/entrypoint.sh

ENTRYPOINT ["/app/bin/entrypoint.sh"]

CMD ["uv", "run", "python", "-m", "trading.database.finance.build_corporate_info", "--database", "test"]
