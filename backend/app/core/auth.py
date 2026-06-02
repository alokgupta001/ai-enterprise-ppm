from jose import jwt

from datetime import datetime
from datetime import timedelta

from app.core.config import SECRET_KEY
from app.core.config import ALGORITHM


def create_access_token(data: dict):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(hours=1)

    payload.update(
        {"exp": expire}
    )

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token