from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from db import get_conn
from security import (
    hash_password,
    verify_password,
    validate_email_domain,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# リクエストモデル
# =========================
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# =========================
# 登録 API
# users(id SERIAL PK, email TEXT UNIQUE, password TEXT, created_at TIMESTAMP)
# =========================
@app.post("/register")
def register(req: RegisterRequest):
    if not validate_email_domain(req.email):
        raise HTTPException(status_code=400, detail="Email domain does not exist")

    conn = get_conn()
    cur = conn.cursor()

    try:
        # email 重複チェック
        cur.execute("SELECT 1 FROM users WHERE email = %s", (req.email,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="Email already registered")

        password_hash = hash_password(req.password)

        # ✅ 今のDB定義に合わせて INSERT（password_hash じゃなく password）
        cur.execute(
            """
            INSERT INTO users (email, password)
            VALUES (%s, %s)
            RETURNING id
            """,
            (req.email, password_hash),
        )
        user_id = cur.fetchone()[0]
        conn.commit()

        return {"status": "registered", "user_id": user_id}

    finally:
        cur.close()
        conn.close()

# =========================
# ログイン API
# =========================
@app.post("/login")
def login(req: LoginRequest):
    conn = get_conn()
    cur = conn.cursor()

    try:
        # ✅ password_hash じゃなく password を取る
        cur.execute("SELECT id, password FROM users WHERE email = %s", (req.email,))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_id, password_hash = row

        if not verify_password(req.password, password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return {"status": "login success", "user_id": user_id}

    finally:
        cur.close()
        conn.close()