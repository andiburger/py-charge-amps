FROM python:3.13-slim

RUN apt-get update && apt-get install -y gcc python3-dev
# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Start with Hypercorn (async production server)
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:5000"]