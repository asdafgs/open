from flask import Flask, jsonify
from uuid import uuid4
import json
import requests
import os
from proof_of_work import get_pow_token

app = Flask(__name__)

current_parameters = None

def generate_id():
    return str(uuid4())

def generate_payload(data, flow):
    data['id'] = generate_id()
    data['flow'] = flow
    return json.dumps(data)

def fetch_requirements(flow, pow_token):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url="https://chatgpt.com/backend-api/sentinel/req",
                data=generate_payload({'p': pow_token}, flow),
            )
            result = response.json()
            return result, True
        except requests.exceptions.RequestException as err:
            if attempt >= 2:
                return generate_payload({'e': str(err)}, flow), False

def refresh_token(flow):
    pow_token = get_pow_token()
    response, _ = fetch_requirements(flow, pow_token)
    if not _:
        return response

    try:
        payload = generate_payload({
            'p': pow_token,
            't': response.get("turnstile", {}).get('dx', ""),
            'c': response.get('token')
        }, flow)
        return payload
    except Exception as err:
        failure = generate_payload({'e': str(err), 'p': pow_token}, flow)
        return failure

def get_sentinel_token():
    flow = 'sora_create_task'
    token = refresh_token(flow)  # 这里可以使用 'OpenAI-Sentinel-Token' 头部
    return token

@app.route('/get_sentinel_token', methods=['GET'])
def get_sentinel_token_route():
    return jsonify(get_sentinel_token())

# 新增的 '/' 路由
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "欢迎来到 Sentinel Token API!", "status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
