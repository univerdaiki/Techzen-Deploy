FROM python:3.11

WORKDIR /app

RUN pip install \
    fastapi \
    uvicorn \
    psycopg2-binary \
    pydantic[email] \
    dnspython \
    bcrypt

COPY main.py .
COPY db.py .
COPY security.py .
COPY templates ./templates

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
