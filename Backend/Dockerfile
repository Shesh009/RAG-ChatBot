FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5001

ENV GEMINI_API_KEY=${GEMINI_API_KEY}

CMD ["python", "app.py"]
