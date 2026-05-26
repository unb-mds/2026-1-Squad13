#!/bin/bash
set -e

echo "Aplicando migrations Alembic..."
docker compose run --rm -T backend uv run alembic upgrade head
echo "Migrations concluídas com sucesso."
