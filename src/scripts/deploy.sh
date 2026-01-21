#!/bin/bash
set -e  # Exit on error

# Load environment variables
if [ -f .env ]; then
    set -a
    . ./.env
    set +a
else
    echo "Error: .env file not found."
    exit 1
fi

if [ -z "${DEPLOY_USER:-}" ] || [ -z "${DEPLOY_SERVER:-}" ] || [ -z "${DEPLOY_PATH:-}" ]; then
    echo "Error: DEPLOY_USER, DEPLOY_SERVER, and DEPLOY_PATH must be set in .env"
    exit 1
fi

if [ ! -d dist ]; then
    echo "Error: dist/ not found. Run npm run build first."
    exit 1
fi

# Deploy using rsync
echo "🚀 Deploying files to production server..."
rsync -avz --progress --delete dist/ "${DEPLOY_USER}@${DEPLOY_SERVER}:${DEPLOY_PATH}"

echo "✅ Deployment complete!"
echo "🌐 Live URL: https://MinistriesForChrist.net/games/"
