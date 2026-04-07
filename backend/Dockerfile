FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATABASE_URL=sqlite:////app/data/dyslexia.db \
    HOST=0.0.0.0 \
    PORT=5001

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libsndfile1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/uploads/handwriting /app/uploads/audio

EXPOSE 5001

CMD ["gunicorn", "-b", "0.0.0.0:5001", "run:app"]