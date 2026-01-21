from app import create_app
from app.socketio_ext import socketio

app = create_app()


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
