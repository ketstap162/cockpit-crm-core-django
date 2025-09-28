# Cockpit CRM Core (Django)

## Overview
This project implements the **Cockpit CRM Core** as the foundation for a modular **Management Cockpit**.  
The CRM serves as the central module, designed to support modular, tether-able extensions (e.g., Money Markets, Portfolio Management, Risk, Compliance).  
All modules share common **SCD Type 2 (Slowly Changing Dimension)** semantics, ensuring consistency, reproducibility, and auditability across the system.

The solution follows the principles outlined in the **Advanced Technical Assignment**:
- Modular architecture
- In-table **SCD2 versioning**
- **Database-first constraints**
- **Idempotent ingestion and update semantics**
- **Clean DRF APIs**

---

## Features
### SCD2 Versioning
- Source: `core/models/scd2`
- Provides a flexible interface to apply SCD2 versioning to every model.
- **valid_from / valid_to / is_current** columns integrated into the core tables.
- PostgreSQL **GiST exclusion constraints** are used to prevent overlaps.
- **Idempotent ingestion** via hash_diff to detect duplicates.
- **Transactional transitions**: close the current row, open a new row.

### Ingestion & Update Semantics
- **Batch ingestion** via management commands.
- **Real-time updates** via the service layer.
- **As-of correctness** guaranteed for queries.
- Idempotent: repeated ingestion of identical payloads does not create duplicate rows.

### API (Django REST Framework)
- `GET /api/v1/entities` – List with filters (`q`, `type`, `detail_code`).
- `GET /api/v1/entities/{entity_uid}` – Current snapshot of an entity.
- `POST /api/v1/entities` – Create a new entity (first version).
- `PATCH /api/v1/entities/{entity_uid}` – Apply updates (SCD2 transitions).
- `GET /api/v1/entities/{entity_uid}/history` – Full history of an entity and its details.
- `GET /api/v1/entities-asof?as_of=YYYY-MM-DD` – Snapshot as of a given date.
- `GET /api/v1/diff?from=YYYY-MM-DD&to=YYYY-MM-DD` – Changes grouped by entity and field.

### Audit & Security
- **Audit log** records every change: timestamp, before/after values.
- **Row-level timestamps**: `created_at`, `updated_at`.
- **Token-based authentication** (future-ready for RBAC).
- Prepared for **PII handling guidelines**.

### Performance & Indexing
- Partial unique indexes for current rows.
- `btree_gist` extension used for GiST exclusion constraints.
- Covering indexes for frequent queries.

---

## Apps
The apps are divided into different groups:
- **Core:** Stores global settings and concepts for other apps in this project.  
- **CRM:** The main management system for other apps.  
  Example: `cockpit`
- **Tetherable apps:** Apps that can be deployed separately but share the same project core.  
  Example: `entities`
- **Technical apps:** Apps that can connect to other apps and have no deployment settings.  
  Example: `auth`

Each app inherits its `settings.py` from the `core` app.

### Cockpit
The Cockpit app is an app manager that allows controlling all project apps.

### Entities
The `entities` app is an example to demonstrate how to set up new apps.  
Models in this app can be defined as abstract and allow inheritance by other models.

It provides the Entities API with OpenAPI documentation.

### Entities app models:
- **Entity**
  - Represents a `Person`, `Institution`, or other.
  - Versioned in-place using `valid_from`, `valid_to`, and `is_current`.
  - Constraints enforce a single current row per `uuid` and prevent overlapping validity windows.

- **Entity Type**
  - Defines the type of entity (`PERSON`, `INSTITUTION`, ...).
  - Provides extensibility for future modules.

- **Entity Detail**
  - Stores versioned detail records.
  - Constraints enforce a single current row per `(entity_uuid, detail_code)` and prevent overlapping validity windows.
  - Uses `hashdiff` to ensure idempotency.

---

## Tech Stack
- **Python** 3.11+
- **Django** 5.x
- **Django REST Framework**
- **PostgreSQL** 14+ (with `btree_gist`)
- **pytest + pytest-django**
- **docker-compose** (local development)

---

## Setup Instructions
Copy the contents of the `.env.sample` files to `.env` files in the following directories:
```bash
<root>
<root>/cockpit/config
<root>/entities/config
```

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development outside Docker)

### Local Development
```bash
# Clone the repository
git clone https://github.com/ketstap162/cockpit-crm-core-django.git
cd cockpit-crm-core-django

# Build services
docker-compose build

# Start services
docker-compose up

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser (for Django Admin)
docker-compose exec web python manage.py createsuperuser
```

## Scripts

### Access to containers
```bash
# To run commands in service containers, use:
docker-compose exec <service_name> <command>

# For example:
docker-compose exec cockpit python manage.py createsuperuser
```

### Django commands
Provides Django management commands.  
Use with `docker-compose exec <service_name>`.

```bash
# Create a superuser for cockpit
python manage.py createsuperuser

# Make database migrations
# Optional: specify <app_name> to create migrations for a specific app
python manage.py makemigrations <app_name>

# Apply migrations
python manage.py migrate
```

## Testing
> **Note**
> It is recommended to run tests for each app in its corresponding container.  
> Each app has its own set of tests that target its specific URLs, which may not exist in the `cockpit` or other modules.


```bash
# Run all tests
poetry run pytest

# Run only the tests that failed in the previous run
poetry run pytest --lf

# Run tests for a specific app
poetry run pytest entities/v1/tests/

# Run tests inside a Docker container
docker-compose exec <service_name> poetry run pytest

# For example:
docker-compose exec entities poetry run pytest entities/v1/tests/
```

## Service access

| Service                  | URL                                |
|--------------------------|------------------------------------|
| Cockpit                  | http://127.0.0.1:8000/             |
| Entities API             | http://127.0.0.1:8001/api/v1       |
| Entities API Swagger     | http://127.0.0.1:8001/docs         |
| Entities API Redoc       | http://127.0.0.1:8001/redoc        |
