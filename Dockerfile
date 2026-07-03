FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv --no-cache-dir && \
    uv sync --frozen --no-dev

COPY . .

EXPOSE 5000

CMD ["uv", "run", "flask", "--app", "main", "run", "--host=0.0.0.0", "--port=5000"]