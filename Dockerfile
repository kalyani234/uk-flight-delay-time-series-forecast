FROM python:3.11-slim

WORKDIR /app

# System deps for numpy/scipy/statsmodels/matplotlib on Debian slim (ARM safe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy code
COPY . /app

# Entrypoint pipeline script
COPY infra/entrypoint.sh /app/infra/entrypoint.sh
RUN chmod +x /app/infra/entrypoint.sh

EXPOSE 8000

CMD ["/app/infra/entrypoint.sh"]
