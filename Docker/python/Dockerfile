FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY respect-backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN useradd --create-home --uid 10001 respect && mkdir -p /app/data && chown respect:respect /app/data
COPY --chown=respect:respect respect-backend/ ./
USER respect
EXPOSE 8000
# One worker serializes tournament capacity and result mutations.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
