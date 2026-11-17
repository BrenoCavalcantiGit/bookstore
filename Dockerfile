# Imagem base com Python
FROM python:3.13-slim

# Evita arquivos .pyc e mostra os logs do Python direto no terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Pasta de trabalho dentro do container
WORKDIR /app

# Instala o Poetry
RUN pip install --no-cache-dir poetry

# Copia só os arquivos de dependências primeiro (aproveita o cache do Docker)
COPY pyproject.toml poetry.lock ./

# Instala as dependências do projeto sem criar ambiente virtual
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copia o restante do projeto
COPY . .

# Porta usada pelo servidor do Django
EXPOSE 8000

# Aplica as migrações e sobe o servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
