# Install uv
FROM python:3.12-slim
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create working directory
RUN mkdir -p /usr/local/src/app
# Add source(s)
COPY . /usr/local/src/app
# Enter working directory
WORKDIR /usr/local/src/app
    
RUN uv sync --locked

# Run as non-root user
RUN adduser physrisk-api
USER physrisk-api

# Enable communication via port 8081
EXPOSE 8081

# Add venv into PATH
ENV PATH="/usr/local/src/app/.venv/bin:$PATH"

# Run FastAPI application
CMD ["fastapi", "run", "src/physrisk_api/app/main.py", "--port", "8081", "--workers", "1"]
