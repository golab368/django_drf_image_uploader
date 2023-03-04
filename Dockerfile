# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app_docker

# Copy the requirements file into the container at /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y libpq-dev

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /app
COPY api_images .

# Run migrations and collect static files
RUN python manage.py migrate --noinput \
    && python manage.py collectstatic --noinput

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
