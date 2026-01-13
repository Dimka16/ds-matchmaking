from app import create_app

app = create_app()


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # IMPORTANT: host must be 0.0.0.0 so Docker can expose it
    app.run(host="0.0.0.0", port=5000, debug=True)
