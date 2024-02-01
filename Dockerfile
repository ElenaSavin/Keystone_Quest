# Base image with Python 3.x
FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    samtools \
    # Other system dependencies you may need

# Set working directory
WORKDIR /app

# Copy requirements.txt file (if any)
COPY requirements.txt requirements.txt

# Install Python libraries
RUN pip install -r requirements.txt

# Copy your application code
COPY . .

# CMD ["python", "app.py"]
