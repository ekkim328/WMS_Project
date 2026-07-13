FROM node:22-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
COPY backend/ai_requirements.txt ./backend/ai_requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir -r backend/ai_requirements.txt

COPY backend ./backend
COPY korean_ecommerce_outbound_2022_2025_with_categories.csv ./backend/data/korean_ecommerce_outbound_2022_2025_with_categories.csv
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

WORKDIR /app/backend

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
