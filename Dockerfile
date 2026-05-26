# ════════════════════════════════════════════════════
# InstaShift – Dockerfile
# Multi-stage build for a lean production image.
# ════════════════════════════════════════════════════

# ── Stage 1: build ───────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies into a prefix
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime ─────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="InstaShift Bot" \
      description="Discord bot that mirrors Instagram feeds" \
      version="1.0.0"

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy source code
COPY bot/ ./bot/

# NOTA: VOLUME eliminado para compatibilidad con Railway

# Ejecutar como root (necesario para Railway sin volumen)
# Si quieres usar volumen, descomenta las líneas de abajo y comenta USER root
USER root

# Environment defaults (override with docker run -e or .env)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
# DB_PATH removido - usar variables de entorno DB_* para MySQL remoto
# SESSION_PATH removido - sesiones se guardan en BD, no archivos locales
    LOG_LEVEL=INFO

CMD ["python", "-m", "bot.main"]

# ========================= NOTA SOBRE ALMACENAMIENTO ==========================
# Este Dockerfile está optimizado para Railway (sin volúmenes persistentes).
# Todos los datos se almacenan en:
#   - Base de datos: MySQL remoto en Hostinger
#   - Sesiones: Tabla instaswift_ig_sessions en la BD (sin archivos locales)
# Esto asegura que el bot funcione correctamente en Railway y otros PaaS.
# ============================================================================