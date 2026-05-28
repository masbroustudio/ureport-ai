.PHONY: help install dev-up dev-down api-dev web-dev api-test lint format

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd apps/api && uv sync
	cd apps/web && pnpm install

dev-up: ## Start infrastructure (Docker)
	docker compose -f infra/docker/compose.dev.yml up -d

dev-down: ## Stop infrastructure
	docker compose -f infra/docker/compose.dev.yml down

api-dev: ## Start backend dev server
	cd apps/api && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web-dev: ## Start frontend dev server
	cd apps/web && pnpm dev

api-test: ## Run backend tests
	cd apps/api && uv run pytest tests/ -v

lint: ## Lint all code
	cd apps/api && uv run ruff check .
	cd apps/web && pnpm lint

format: ## Format all code
	cd apps/api && uv run ruff format .
	cd apps/web && pnpm format
