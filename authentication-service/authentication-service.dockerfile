# Use the official Python 3.11 image as a base
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY . /app

# Copy the wait-for-it.sh script into the container
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Set environment variable for Alembic configuration file
ENV ALEMBIC_CONFIG=/app/alembic.ini

# Expose the application port
EXPOSE 8000

# Start the app after waiting for the database
CMD ["sh", "-c", "/wait-for-it.sh db:5432 -- alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
