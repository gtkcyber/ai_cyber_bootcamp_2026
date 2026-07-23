FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for scientific Python + plotting
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    pandas==2.2.2 \
    streamlit==1.37.1 \
    sqlglot==27.14.0 \
    lark==1.2.2 \
    matplotlib==3.9.2 \
    seaborn==0.13.2 \
    pyyaml==6.0.2

# Install PandasAI (PyPI if available, otherwise GitHub main)
RUN pip install --no-cache-dir pandasai==2.2.0 || \
    pip install --no-cache-dir "git+https://github.com/gventuri/pandas-ai.git@main"

# Copy app code (overridden by volume mount at runtime)
COPY app.py /app/app.py

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
