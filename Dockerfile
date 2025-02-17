FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tudo (incluindo app.py e spiders/)
COPY . /app

# Expõe a porta que o Flask usará
EXPOSE 5000

# Comando final para rodar app.py
CMD ["python", "app.py"]
