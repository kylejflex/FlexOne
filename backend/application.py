from flask import Flask, jsonify

application = Flask(__name__)

@application.get("/")
def root():
    return jsonify(status="ok", service="mcp-backend")

@application.get("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8000, debug=True)
