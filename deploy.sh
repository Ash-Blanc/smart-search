#!/bin/bash

# Create requirements.txt from uv
uv pip compile pyproject.toml -o requirements.txt

# Create Procfile for deployment
echo "web: uvicorn api.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Git setup
git init
git add .
git commit -m "Initial deployment"

echo "Ready to deploy! Push to GitHub and connect to Railway/Render"