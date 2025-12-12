# api/create.py
import os, json
from itsdangerous import TimestampSigner
from urllib.parse import quote_plus

def handler(request):
    # defensive parsing for Vercel request object
    try:
        body = request.body or b""
        if isinstance(body, bytes):
            data = json.loads(body.decode("utf-8") or "{}")
        else:
            # sometimes request.body is already str
            data = json.loads(body)
    except Exception:
        return {"statusCode": 400, "body": "Invalid JSON"}

    file_path = data.get("file_path")
    owner_id = data.get("owner_id", "")

    if not file_path:
        return {"statusCode": 400, "body": "file_path missing"}

    secret = os.environ.get("SIGNING_SECRET")
    if not secret:
        return {"statusCode": 500, "body": "SIGNING_SECRET missing"}

    try:
        expire = int(os.environ.get("EXPIRE_SECONDS", "3600"))
    except Exception:
        expire = 3600

    signer = TimestampSigner(secret)

    payload = json.dumps({"file_path": file_path, "owner_id": owner_id})
    try:
        signed = signer.sign(payload.encode()).decode()
    except Exception as e:
        return {"statusCode": 500, "body": f"sign error: {str(e)}"}

    token = quote_plus(signed)

    return {
        "statusCode": 201,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "link": f"/api/redirect?token={token}",
            "token": token,
            "expires_in": expire
        })
    }


