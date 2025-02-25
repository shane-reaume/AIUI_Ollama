FROM node:18.16 AS frontend_builder

WORKDIR /frontend

COPY ./frontend/package.json ./frontend/yarn.lock ./

RUN yarn install --frozen-lockfile

COPY ./frontend/ ./

RUN yarn build

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10-slim

WORKDIR /

ENV MAX_WORKERS=5

RUN apt-get update && apt-get install -y ffmpeg wget unzip

COPY ./backend/requirements.txt /tmp/

RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

# Download Vosk model for English
RUN mkdir -p /app/vosk-model && \
    wget -O /tmp/vosk-model-small-en-us-0.15.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip && \
    unzip /tmp/vosk-model-small-en-us-0.15.zip -d /tmp/ && \
    mv /tmp/vosk-model-small-en-us-0.15/* /app/vosk-model/ && \
    rm -rf /tmp/vosk-model-small-en-us-0.15 /tmp/vosk-model-small-en-us-0.15.zip

COPY ./backend /app

COPY --from=frontend_builder /frontend/dist /app/frontend/dist
