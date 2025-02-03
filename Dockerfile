# Base Image
FROM python:3.9

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Flask
EXPOSE 5000

# Start the server
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers=4", "main:app"]
