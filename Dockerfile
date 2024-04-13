FROM python:3.11-slim-bookworm
WORKDIR /app
COPY docker/requirements.txt .
RUN pip install -r requirements.txt
COPY *.py /app/
CMD ["python3", "service_runner.py"]