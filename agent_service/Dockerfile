# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app
ENV PYTHONPATH /app/src

# Copy the requirements file
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Set environment variables (if needed)
# ENV FLASK_APP=your_app.py

# Define the command to start the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
# CMD ["python", "your_app.py"]  # Or "gunicorn --bind 0.0.0.0:5000 your_app:app" for production


# FROM python:3.11-slim-buster

# WORKDIR /app

# # Install system dependencies, including build tools and wget
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     wget \
#     ca-certificates \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Download and install a newer version of SQLite
# RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3450100.tar.gz && \
#     tar xvf sqlite-autoconf-3450100.tar.gz && \
#     cd sqlite-autoconf-3450100 && \
#     ./configure --prefix=/usr/local && \
#     make install && \
#     ldconfig

# # Verify the SQLite version
# RUN sqlite3 --version

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# # ENV PYTHONPATH=/app

# CMD ["uvicorn", "api.api_router:app", "--host", "0.0.0.0", "--port", "8000"]




# Stage 1 — Builder
# FROM python:3.11-slim-bullseye AS builder

# WORKDIR /app
# ENV PYTHONPATH /app/src

# # Install build dependencies (only in builder stage)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements first for caching
# COPY requirements.txt .

# # Install Python dependencies into a separate folder
# RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# # Stage 2 — Runtime
# FROM python:3.11-slim-buster

# WORKDIR /app
# ENV PYTHONPATH /app/src

# # Copy installed packages from builder
# COPY --from=builder /install /usr/local

# # Copy your application code
# COPY . .

# # Expose port
# EXPOSE 8000

# # Run app
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
