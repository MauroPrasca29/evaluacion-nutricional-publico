# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir alembic psycopg2-binary

# Copiar el código
COPY . .

# Crear carpetas necesarias
RUN mkdir -p uploads logs

# Railway ignorará esto, pero no molesta:
EXPOSE 8000

# Healthcheck dinámico usando $PORT
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Comando final usando $PORT real
CMD ["sh", "-c", "cd db_sistema_nutricion && alembic upgrade head && cd .. && uvicorn main:app --host 0.0.0.0 --port $PORT"]
