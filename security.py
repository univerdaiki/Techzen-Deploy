import bcrypt
import uuid
import dns.resolver
from pydantic import EmailStr

# user_id を自動生成
def generate_user_id():
    return uuid.uuid4()

# パスワードをハッシュ化
def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

# パスワード照合
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password.encode(),
        hashed.encode()
    )

# メールドメインが実在するかチェック（MXレコード）
def validate_email_domain(email: EmailStr):
    domain = email.split("@")[1]
    try:
        dns.resolver.resolve(domain, "MX")
        return True
    except Exception:
        return False
