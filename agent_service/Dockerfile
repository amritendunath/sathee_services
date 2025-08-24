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
EXPOSE 8001


# Define the command to start the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]


