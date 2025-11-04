#!/bin/bash

# Alembic migration helper script

# Activate virtual environment
source venv/bin/activate

case "$1" in
    "init")
        echo "Creating initial migration..."
        alembic revision --autogenerate -m "Initial migration"
        ;;
    "create")
        if [ -z "$2" ]; then
            echo "Usage: ./migrate.sh create 'migration message'"
            exit 1
        fi
        echo "Creating new migration: $2"
        alembic revision --autogenerate -m "$2"
        ;;
    "upgrade")
        echo "Running migrations..."
        alembic upgrade head
        ;;
    "downgrade")
        if [ -z "$2" ]; then
            echo "Downgrading by 1 revision..."
            alembic downgrade -1
        else
            echo "Downgrading to revision: $2"
            alembic downgrade "$2"
        fi
        ;;
    "current")
        echo "Current database revision:"
        alembic current
        ;;
    "history")
        echo "Migration history:"
        alembic history --verbose
        ;;
    "show")
        if [ -z "$2" ]; then
            echo "Usage: ./migrate.sh show <revision>"
            exit 1
        fi
        echo "Showing migration: $2"
        alembic show "$2"
        ;;
    *)
        echo "Usage: ./migrate.sh {init|create|upgrade|downgrade|current|history|show}"
        echo ""
        echo "Commands:"
        echo "  init                    - Create initial migration"
        echo "  create 'message'        - Create new migration with message"
        echo "  upgrade                 - Run all pending migrations"
        echo "  downgrade [revision]    - Downgrade to revision (or -1 for previous)"
        echo "  current                 - Show current database revision"
        echo "  history                 - Show migration history"
        echo "  show <revision>         - Show specific migration details"
        exit 1
        ;;
esac
