#!/bin/bash
set -e

INSTANCE_IP="$1"
KEY_FILE="$2"

if [ -z "$INSTANCE_IP" ] || [ -z "$KEY_FILE" ]; then
    echo "Usage: $0 <instance-ip> <key-file.pem>"
    exit 1
fi

echo "Deploying RepoDoc AI backend to EC2 instance: $INSTANCE_IP"

scp -i "$KEY_FILE" -o StrictHostKeyChecking=no \
    deploy/repodoc-ai.service \
    ec2-user@"$INSTANCE_IP":/home/ec2-user/repodoc-ai.service

ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$INSTANCE_IP" << 'EOF'
    sudo mkdir -p /home/ec2-user/repodoc-ai/backend/deploy
    sudo cp /home/ec2-user/repodoc-ai.service /etc/systemd/system/repodoc-ai.service
    sudo systemctl daemon-reload
    sudo systemctl enable repodoc-ai.service
    sudo systemctl restart repodoc-ai.service
    sudo systemctl status repodoc-ai.service
EOF

echo "Deployment complete. Backend running on http://$INSTANCE_IP:8000"