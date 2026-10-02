FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir gunicorn langchain-google-genai langgraph python-dotenv scikit-learn

COPY agent ./agent
COPY backend ./backend
COPY prompts ./prompts
COPY rag ./rag
COPY data ./data

WORKDIR /app/backend

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py import_consumer_act && python manage.py create_chunks && python manage.py build_tfidf_index && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]