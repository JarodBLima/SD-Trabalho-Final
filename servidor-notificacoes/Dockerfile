FROM python:3.9-slim-buster
WORKDIR /app
COPY . .
COPY certificados /app/certificados
EXPOSE 6000
CMD ["python", "app.py"]