# --- Build stage ---
FROM python:3.13-alpine AS build

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Final stage ---
FROM python:3.13-alpine

WORKDIR /app
COPY . /app
COPY --from=build /install /usr/local

EXPOSE 5000
CMD ["sh", "-c", "hypercorn app:app --bind 0.0.0.0:5000"]