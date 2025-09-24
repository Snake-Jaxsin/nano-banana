FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (ultra-fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy requirements files
COPY requirements.txt .

# Install packages using both uv and pip as requested
RUN uv pip install -r requirements.txt
RUN pip install google-generativeai pillow python-dotenv streamlit-drawable-canvas

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8504

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8504/_stcore/health

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8504", "--server.address=0.0.0.0"]