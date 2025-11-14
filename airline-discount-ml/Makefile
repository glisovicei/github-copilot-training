# Makefile for airline-discount-ml project
# Provides convenient commands for common tasks

.PHONY: help setup install test clean run-notebook lint format db-init

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Complete setup (create venv, install deps, setup db)
	@bash setup.sh

install: ## Install package and dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov

run-notebook: ## Start Jupyter Lab
	jupyter lab

lint: ## Run linter
	flake8 src tests

format: ## Format code with black
	black src tests

db-init: ## Initialize database
	python -c "from src.data.database import init_database; init_database()"

db-sample: ## Load sample data into database
	python -c "from src.data.database import load_sample_data; load_sample_data()"

train: ## Train the model
	python src/training/train.py

evaluate: ## Evaluate the model
	python src/training/evaluate.py
