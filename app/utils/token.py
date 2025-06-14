from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def generate_verification_token(email: str):
    return serializer.dumps(email, salt="email-confirm")

def verify_token(token: str, expiration=3600):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=expiration)
    except Exception:
        return None
    return email
