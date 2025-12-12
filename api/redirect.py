# api/redirect.py
import os, json
from urllib.parse import unquote_plus
from itsdangerous import TimestampSigner, SignatureExpired, BadSignature

def handler(request):
    # get token from query params
    try:
        token = None
        if hasattr(request, "query_params"):
            token = request.query_params.get("token")
        else:
            # fallback parse raw query string
            qs = request.scope.get("query_string", b"").decode() if hasattr(request, "scope") else ""
            # simple parse
            for part in qs.split("&"):
                if part.startswith("token="):
                    token = part.split("=",1)[1]
                    break
    except Exception:
        token = None

    if not token:
        return {"statusCode": 400, "body": "Token missing"}

    try:
        token = unquote_plus(token)
    except:
        pass

    secret = os.environ.get("SIGNING_SECRET")
    if not secret:
        return {"statusCode": 500, "body": "SIGNING_SECRET missing"}

    try:
        expire = int(os.environ.get("EXPIRE_SECONDS", "3600"))
    except:
        expire = 3600

    signer = TimestampSigner(secret)

    try:
        raw = signer.unsign(token, max_age=expire)
    except SignatureExpired:
        return {"statusCode": 410, "body": "Link expired"}
    except BadSignature:
        return {"statusCode": 400, "body": "Invalid token"}
    except Exception as e:
        return {"statusCode": 500, "body": f"unsign error: {str(e)}"}

    try:
        payload = json.loads(raw.decode())
        file_path = payload.get("file_path")
    except Exception:
        return {"statusCode": 400, "body": "Bad payload"}

    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        return {"statusCode": 500, "body": "BOT_TOKEN missing"}

    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"

    return {"statusCode": 302, "headers": {"Location": download_url}}



