
FROM python:3-slim
ENV PYTHONUNBUFFERED 1

WORKDIR /app
# requirements.txt should be present in the same directory from we run docker build command
COPY requirements.txt .

RUN apt-get update -y && \
	apt-get upgrade -y && \
	apt-get install -y vim && \
    apt-get install -y libpq-dev && \
    apt-get install -y python3-dev && \
    apt-get install -y gcc && \
	pip install -r requirements.txt --no-cache-dir && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*
	
# Copy all file from context to /app directory	
COPY . .

VOLUME /app/data

CMD  python3 manage.py makemigrations && \
    python3 manage.py migrate && \
    python3 manage.py collectstatic --noinput && \
    python manage.py runserver 0.0.0.0:8000