# Base image with Python 3.10
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    samtools curl # Add other system dependencies as needed
# Set working directory
WORKDIR /app
RUN pip install --upgrade pip && \
    pip3 install oci-cli

COPY private.pem .
# Set environment variables for OCI CLI to use
ENV AWS_ACCESS_KEY_ID= \
    AWS_SECRET_ACCESS_KEY=  \
    AWS_DEFAULT_REGION=us-east-1

# Create a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy requirements.txt first for caching optimization
COPY requirments.txt requirments.txt

# Install Python dependencies within the virtual environment
RUN pip3 install --no-cache-dir -r requirments.txt

# Copy application code
COPY . .

# Expose necessary ports (if applicable)
# EXPOSE 8000  # Example

CMD ["sleep", "infinity"]
