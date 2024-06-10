# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    context = ("cert.crt", "cert.key")
    app.run(debug=False, host="0.0.0.0", port=5001, ssl_context=context)
