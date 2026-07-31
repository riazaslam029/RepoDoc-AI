FROM python:3.12-slim AS builder

WORKDIR /app

COPY backend/requirements-prod.txt .
RUN pip install --no-cache-dir --user -r requirements-prod.txt

FROM python:3.12-slim AS production

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY backend/ .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PORT=8080

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]