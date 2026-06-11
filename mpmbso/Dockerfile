FROM python:3.12-slim

WORKDIR /app

# Variable de entorno clave para que Python reconozca la carpeta 'src' como módulo
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY src/ /app/src/
COPY tests/ /app/tests/

RUN mkdir -p /app/output

CMD ["python", "src/main.py"]
