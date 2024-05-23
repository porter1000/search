from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/proxy/<path:url>', methods=['GET'])
def proxy(url):
    target_url = f'http://{url}'
    headers = {key: value for key, value in request.headers if key != 'Host'}
    response = requests.get(target_url, headers=headers, params=request.args)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in response.raw.headers.items() if name.lower() not in excluded_headers]

    # Modify headers to bypass CSP
    headers.append(('Access-Control-Allow-Origin', '*'))
    headers.append(('Content-Security-Policy', "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:"))

    return Response(response.content, response.status_code, headers)

if __name__ == "__main__":
    app.run(port=8080)
