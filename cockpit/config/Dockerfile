# crm/Dockerfile

FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root

COPY .. .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
