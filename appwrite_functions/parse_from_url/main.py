import os
import sys
import json
from http import HTTPStatus

# Add the current directory to sys.path to allow importing from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.handlers.parse_from_url import parse_from_url_handler

class AppwriteLogger:
    def __init__(self, context):
        self.context = context

    def info(self, msg, *args):
        self.context.log(str(msg) % args if args else str(msg))

    def warning(self, msg, *args):
        self.context.log(f"WARNING: {str(msg) % args if args else str(msg)}")

    def error(self, msg, *args):
        self.context.error(str(msg) % args if args else str(msg))

def main(context):
    logger = AppwriteLogger(context)
    
    if context.req.method != "POST":
        return context.res.send("Method not allowed", 405)

    try:
        if isinstance(context.req.body, str):
            body = json.loads(context.req.body)
        else:
            body = context.req.body

        url = body.get("url")
        user_id = body.get("user_id")
    except Exception as e:
        logger.error(f"Error parsing body: {e}")
        return context.res.json({"msg": "Invalid JSON body"}, 400)

    status, response = parse_from_url_handler(url, user_id, logger)
    
    return context.res.json(response, status.value)
