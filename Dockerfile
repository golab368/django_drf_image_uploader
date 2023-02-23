# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /api_docker
WORKDIR /api_images

# Copy the requirements file into the container at /api_docker
COPY requirements.txt /api_images/

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install Django
RUN pip install Django

# Copy the current directory contents into the container at /api_docker
COPY . /api_images/

# Run app.py when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
