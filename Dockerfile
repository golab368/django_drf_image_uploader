FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y redis

# Set the environment variables for Redis Cloud
ENV REDIS_URL="redis://default:zfa0amh1MseYdj4tMx9u1Sp3u3ZnTvW0@redis-15540.c250.eu-central-1-1.ec2.cloud.redislabs.com:15540"

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y libpq-dev \
    && apt-get -y install gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . .

# Run migrations and collect static files
RUN python manage.py migrate --noinput \
    && python manage.py collectstatic --noinput

# Copy the start script into the container
COPY start.sh .

# Make the start script executable
RUN chmod +x start.sh

# Start Celery and Django
CMD ["./start.sh"]
