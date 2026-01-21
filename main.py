from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, EmailStr, Field
from db import get_conn
from security import (
    generate_user_id,
    hash_password,
    verify_password,
    validate_email_domain
)

app = FastAPI()

# CORSの設定を追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 開発中は一旦すべて許可。本番はフロントのIPを指定
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
# =========================
@app.post("/register")
def register(req: RegisterRequest):
    # メールドメイン実在チェック
    if not validate_email_domain(req.email):
        raise HTTPException(
            status_code=400,
            detail="Email domain does not exist"
        )

    conn = get_conn()
    cur = conn.cursor()

    # email 重複チェック
    cur.execute(
        "SELECT 1 FROM users WHERE email = %s",
        (req.email,)
    )
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    # ✅ UUID → 文字列に変換（ここが超重要）
    user_id = str(generate_user_id())
    password_hash = hash_password(req.password)

    cur.execute(
        """
        INSERT INTO users (user_id, email, password_hash)
        VALUES (%s, %s, %s)
        """,
        (user_id, req.email, password_hash)
    )

    conn.commit()

    cur.close()
    conn.close()

    return {
        "status": "registered",
        "user_id": user_id
    }

# =========================
# ログイン API
# =========================
@app.post("/login")
def login(req: LoginRequest):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id, password_hash FROM users WHERE email = %s",
        (req.email,)
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    user_id, password_hash = row

    if not verify_password(req.password, password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "status": "login success",
        "user_id": user_id
    }