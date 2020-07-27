import logging
import json
import os
from flask import Flask, request
from data.db_session import global_init
from services.handler import Handler

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.config["SECRET_KEY"] = "Marusya"


@app.route('/', methods=["POST"])
def main():
    request_json = request.json
    logging.info(f'Request: {request_json!r}')
    response = {
        'session': request_json['session'],
        'version': request_json['version'],
        'response': {
            'tts': "",
            'text': "",
            'end_session': False
        }
    }
    handler.handle_dialog(request_json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


if __name__ == "__main__":
    global_init("db/Dates.sqlite")
    handler = Handler()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
