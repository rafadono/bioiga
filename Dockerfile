# =============================================================================
# ETAPA 1: Builder (Compilación de Rust y Dependencias de Python)
# =============================================================================
FROM python:3.12-slim as builder

# Instalar herramientas de compilación y Toolchain de Rust
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# Copiar configuración del proyecto y código fuente
COPY pyproject.toml README.md ./
COPY iga_core ./iga_core
COPY bioiga ./bioiga
COPY mpmbso ./mpmbso
COPY mpga ./mpga
COPY mpbfa ./mpbfa
COPY mpbgwo ./mpbgwo
COPY mpbba ./mpbba

# Compilar la extensión binaria en Rust mediante Cargo y pip
RUN cargo build --release --manifest-path iga_core/Cargo.toml
RUN pip install --no-cache-dir build maturin
RUN pip install --no-cache-dir -e .

# =============================================================================
# ETAPA 2: Runner (Imagen Ligera de Producción)
# =============================================================================
FROM python:3.12-slim as runner

WORKDIR /app

# Copiar paquetes instalados y binarios compilados de la etapa builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app /app

EXPOSE 8000

# Comando de inicio del servidor FastAPI sin necesidad del compilador Rust en runtime
CMD ["python", "-m", "uvicorn", "bioiga.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
