# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /

# Copy the requirements file into the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY . .

# Set the environment variables
ENV PYTHONUNBUFFERED=1

# Run the Django development server
CMD ["python", "manage.py", "collectstatic"]

# Expose the default Django port (change if necessary)
EXPOSE 8000

CMD ["gunicorn", "djcms.wsgi", "--bind", "0.0.0.0:8000"]

