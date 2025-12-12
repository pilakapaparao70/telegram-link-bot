import os
import json
from urllib.parse import unquote_plus
from itsdangerous import TimestampSigner, SignatureExpired, BadSignature

def handler(request):
    token = request.query_params.get("token")

    if not token:
        return {"statusCode": 400, "body": "Token missing"}

    token = unquote_plus(token)

    secret = os.environ.get("SIGNING_SECRET")
    if not secret:
        return {"statusCode": 500, "body": "SIGNING_SECRET missing"}

    expire = int(os.environ.get("EXPIRE_SECONDS", "3600"))
    signer = TimestampSigner(secret)

    try:
        raw = signer.unsign(token, max_age=expire)
    except SignatureExpired:
        return {"statusCode": 410, "body": "Link expired"}
    except BadSignature:
        return {"statusCode": 400, "body": "Invalid token"}

    payload = json.loads(raw.decode())
    file_path = payload["file_path"]

    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        return {"statusCode": 500, "body": "BOT_TOKEN missing"}

    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"

    return {
        "statusCode": 302,
        "headers": {"Location": download_url}
    }
