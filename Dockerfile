FROM python:3.13-alpine

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev
# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Start with Hypercorn (async production server)
CMD ["sh", "-c", "hypercorn app:app --bind 0.0.0.0:5000"]