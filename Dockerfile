# Use a lightweight Python 3.8 image
FROM python:3.8-slim

# 1. Install System Dependencies (Required for dlib & opencv)
# We install cmake and compilers so dlib can build properly, 
# but we do it in a single layer to keep the image small.
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    g++ \
    libx11-dev \
    libgtk-3-dev \
    libboost-python-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Set working directory
WORKDIR /app

# 3. Upgrade pip to avoid potential wheel issues
RUN pip install --upgrade pip

# 4. Copy requirements file
COPY requirements.txt .

# 5. Install Python Dependencies
# We install dlib first separately because it's the heaviest
RUN pip install --no-cache-dir dlib

# Install the rest
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the application code
COPY main.py .

# 7. Command to start the server
# Render uses port 10000 by default for web services
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
