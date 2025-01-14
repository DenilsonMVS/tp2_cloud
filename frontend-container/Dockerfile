# Use a Python image as the base image
FROM python:3.9-slim-bullseye

# Set working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port 3000 so that it can be accessed outside the container
EXPOSE 3000

# Run the rule generation script to generate the model
CMD ["flask", "run", "--port", "3000", "--host", "0.0.0.0"]
