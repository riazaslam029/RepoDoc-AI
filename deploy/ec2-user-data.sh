#!/bin/bash
set -e

yum update -y

yum install -y python3 python3-pip python3-venv git nginx

pip3 install --upgrade pip

mkdir -p /home/ec2-user/repodoc-ai

cd /home/ec2-user/repodoc-ai

git clone https://github.com/riazaslam029/RepoDoc-AI.git repo

cd repo/backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cd /home/ec2-user/repodoc-ai/repo/frontend

npm install
npm run build

mkdir -p /home/ec2-user/repodoc-ai/backend/deploy
cp /home/ec2-user/repodoc-ai/repo/backend/deploy/repodoc-ai.service /etc/systemd/system/repodoc-ai.service

cat > /etc/nginx/conf.d/repodoc-ai.conf << 'EOF'
server {
    listen 80;
    server_name _;

    root /home/ec2-user/repodoc-ai/repo/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

CORS_ORIGINS="${CORS_ORIGINS:-https://main.dpj4xk9u0xryq.amplifyapp.com}"

cat > /home/ec2-user/repodoc-ai/repo/backend/.env << EOF
AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307
GITHUB_TOKEN=${GITHUB_TOKEN:-}
CORS_ORIGINS=$CORS_ORIGINS
EOF

sudo systemctl daemon-reload
systemctl enable repodoc-ai.service
systemctl start repodoc-ai.service

systemctl enable nginx
systemctl restart nginx

aws configure set region ap-south-1

cat > /etc/nginx/conf.d/repodoc-ai.conf << 'EOF'
server {
    listen 80;
    server_name _;

    root /home/ec2-user/repodoc-ai/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

CORS_ORIGINS="${CORS_ORIGINS:-https://main.dpj4xk9u0xryq.amplifyapp.com}"

cat > /home/ec2-user/repodoc-ai/backend/.env << EOF
AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307
GITHUB_TOKEN=${GITHUB_TOKEN:-}
CORS_ORIGINS=$CORS_ORIGINS
EOF

sudo systemctl restart repodoc-ai.service

systemctl restart nginx

aws configure set region ap-south-1