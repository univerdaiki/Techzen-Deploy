import os
import psycopg2

def get_conn():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # ローカル用（docker compose）
        return psycopg2.connect(
            host="db",
            dbname="postgres",
            user="postgres",
            password="postgres",
        )
    # 本番用（Render/Railwayなど）
    return psycopg2.connect(database_url)