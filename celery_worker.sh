#!/bin/bash

set -e

echo "Запуск Celery воркера..."
celery -A tasks worker --loglevel=info --concurrency=$(nproc)