import os

# Gunicorn configuration for Render deployment
# Automatically binds to the dynamic PORT assigned by Render
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

workers = 1
threads = 2
timeout = 120
keepalive = 5
loglevel = "info"
accesslog = "-"
errorlog = "-"
