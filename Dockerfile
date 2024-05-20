# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

#Set PYTHONPATH
ENV PYTHONPATH=/app

COPY poetry.lock pyproject.toml docker-entrypoint.sh main.py config.py /app/
RUN poetry install --no-root --no-dev   

# Copy the current directory contents into the container at /app
COPY libs /app/libs/

#Give permissions to run docker-entrypoint.sh
RUN chmod +x "docker-entrypoint.sh"

ENTRYPOINT ["/app/docker-entrypoint.sh"]