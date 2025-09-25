FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (ultra-fast Python package manager)
RUN pip install uv

# Copy requirements files
COPY requirements.txt .

# Install packages
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8504

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8504/_stcore/health

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8504", "--server.address=0.0.0.0"]