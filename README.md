# CI/CD Lab

![CI](https://github.com/your-user/ci-cd-lab/actions/workflows/ci.yml/badge.svg)

A DevOps-focused Flask task API project used to practice CI/CD, Docker, and deployment workflows.

## Project overview
This project includes:
- A Flask-based task API
- SQLite persistence
- Health and version endpoints
- Docker image build and local runtime with Docker Compose
- GitHub Actions CI and manual deploy workflow
- Jenkins pipeline with approval-gated local deploy

## Application capabilities
- `GET /health` — basic health check
- `GET /version` — runtime version and image metadata
- `GET /tasks` — list tasks
- `POST /tasks` — create a task
- `GET /tasks/<id>` — fetch a task
- `PATCH /tasks/<id>` — update a task
- `DELETE /tasks/<id>` — delete a task
- `GET /stats` — task status summary

## Project structure
- `app/main.py` — Flask application
- `app/db.py` — SQLite setup and connection logic
- `tests/test_main.py` — application tests
- `Dockerfile` — application image build
- `docker-compose.yml` — local container runtime
- `Jenkinsfile` — Jenkins pipeline
- `.github/workflows/ci.yml` — GitHub Actions CI workflow
- `.github/workflows/deploy.yml` — GitHub Actions manual deploy workflow
- `requirements.txt` — runtime dependencies
- `requirements-dev.txt` — development and test dependencies

## CI/CD capabilities

### GitHub Actions
- Smoke check
- Flake8 lint
- Pytest
- Python matrix: 3.11 / 3.12
- Pip cache
- Manual trigger
- Path filters
- Concurrency control
- Docker image build
- Container health verification
- Version endpoint verification
- Commit-based Docker image tagging
- Image metadata artifact
- Separate manual deploy workflow

### Jenkins
- Smoke check
- Flake8 lint
- Pytest
- Docker image build
- Container health verification
- Version endpoint verification
- Commit-based Docker image tagging
- Image metadata generation
- Approval-gated local deploy with Docker Compose
- Deployment marker with version and image tracking

## Local development
Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
