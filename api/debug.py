# api/debug.py
import os, json
def handler(request):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "SIGNING_SECRET_set": bool(os.environ.get("SIGNING_SECRET")),
            "BOT_TOKEN_set": bool(os.environ.get("BOT_TOKEN")),
            "EXPIRE_SECONDS": os.environ.get("EXPIRE_SECONDS")
        })
    }
