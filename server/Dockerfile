FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --locked --no-install-project --no-dev

# Copy the application code
COPY ./bot.py ./
COPY ./r2c2 ./r2c2
COPY ./api ./api
COPY ./database ./database
COPY ./processors ./processors

# Create data directory for database
RUN mkdir -p ./data

# Set host to 0.0.0.0 for external access (required for Render)
ENV HOST=0.0.0.0

# Expose port
EXPOSE 7860

# Run the application with host binding
CMD ["uv", "run", "python", "bot.py", "--host", "0.0.0.0"]
