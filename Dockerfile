FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure media_cache directory exists and is writable
RUN mkdir -p media_cache && chmod 777 media_cache

# Ensure config_data.json exists or is writable
# HF Spaces use a non-root user, so we need to make sure the app directory is writable
RUN chmod -R 777 /app

ENV PORT=7860
ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["python", "server.py"]
