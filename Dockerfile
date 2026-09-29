FROM python:3.14-slim 

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --system app && useradd --system --gid app --create-home app
COPY --chown=app:app . .
RUN mkdir -p /app/media /app/staticfiles && chown -R app:app /app/media /app/staticfiles

USER app
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
