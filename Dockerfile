FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN pip install --upgrade pip && \
    pip install poetry

RUN poetry config virtualenvs.create false && \
    poetry install --no-root

COPY . .

CMD ["python", "bot.py"]
