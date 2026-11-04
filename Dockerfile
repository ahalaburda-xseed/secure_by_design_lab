FROM python:3.8

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# No USER instruction: the container runs as root.
CMD ["python", "app.py"]
