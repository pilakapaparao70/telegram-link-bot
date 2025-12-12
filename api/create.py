import os
import json
from itsdangerous import TimestampSigner
from urllib.parse import quote_plus

def handler(request):
    data = request.get_json()

    file_path = data.get("file_path")
    owner_id = data.get("owner_id", "")

    if not file_path:
        return {"statusCode": 400, "body": "file_path missing"}

    secret = os.environ.get("SIGNING_SECRET")
    if not secret:
        return {"statusCode": 500, "body": "SIGNING_SECRET missing"}

    expire = int(os.environ.get("EXPIRE_SECONDS", "3600"))
    signer = TimestampSigner(secret)

    payload = json.dumps({"file_path": file_path, "owner_id": owner_id})
    signed = signer.sign(payload.encode()).decode()

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
