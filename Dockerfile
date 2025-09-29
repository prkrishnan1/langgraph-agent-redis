# Stage 1: Build environment
FROM ghcr.io/astral-sh/uv:0.8.22-python3.13-trixie-slim

# Copy project files
COPY . /app

# Install dependencies using uv
WORKDIR /app

RUN uv venv
RUN /bin/bash -c "source .venv/bin/activate"
RUN uv sync --no-install-project --frozen

# Expose the port your application listens on
EXPOSE 8501

# Run your application
ENTRYPOINT ["/bin/bash", "-c", "source .venv/bin/activate && streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]