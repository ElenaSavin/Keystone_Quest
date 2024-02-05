# Base image with Python 3.10
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    samtools curl # Add other system dependencies as needed
# Set working directory
WORKDIR /app
RUN bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)" \
    mkdir /app/.oci

COPY /home/lena/oracle_creds_for_docker/. ./.oci/.
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
