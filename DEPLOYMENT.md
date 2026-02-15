# Deployment Guide

This guide explains how to deploy the Anonymous Messages application to production.

## Platform-Specific Deployment

### Heroku Deployment

1. **Create Procfile**:
```
web: gunicorn app:app
```

2. **Add gunicorn to requirements.txt** (if deploying to Heroku):
```bash
pip install gunicorn
pip freeze > requirements.txt
```

3. **Deploy**:
```bash
heroku login
heroku create your-app-name
git push heroku main
```

4. **Set environment variables on Heroku**:
```bash
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set DEBUG=false
heroku config:set SECURE_COOKIES=true
```

### Render/Railway/Fly.io (Recommended for Python)

1. **Create runtime.txt**:
```
python-3.11.0
```

2. **Deploy via platform dashboard or CLI**:
- Connect your GitHub repo
- Set environment variables in the platform dashboard
- Platform will automatically run `pip install -r requirements.txt`
- Set start command to: `gunicorn app:app`

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

Create a `docker-compose.yml` for local testing:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=dev-secret-key
      - DEBUG=false
      - SECURE_COOKIES=false
    volumes:
      - ./data:/app/data
```

### Traditional VPS (Ubuntu/Debian)

1. **Setup on server**:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx
git clone your-repo
cd anonymous-messages
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

2. **Create systemd service** (`/etc/systemd/system/anonymous-messages.service`):
```ini
[Unit]
Description=Anonymous Messages Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/anonymous-messages
Environment="PATH=/path/to/anonymous-messages/venv/bin"
Environment="SECRET_KEY=your-secret-key"
Environment="DEBUG=false"
Environment="SECURE_COOKIES=true"
ExecStart=/path/to/anonymous-messages/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

3. **Setup Nginx reverse proxy** (`/etc/nginx/sites-available/anonymous-messages`):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **Setup SSL with Let's Encrypt**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

5. **Enable and start service**:
```bash
sudo systemctl enable anonymous-messages
sudo systemctl start anonymous-messages
```

## Environment Variables for Production

Create a `.env` file (or set these as environment variables):

```
SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_hex(32))">
DEBUG=false
HOST=0.0.0.0
PORT=5000
SECURE_COOKIES=true
```

## Database Migration (Future)

Currently, the app uses a JSON file-based store (`data/store.json`). For production with high traffic, consider migrating to:
- PostgreSQL
- MongoDB
- AWS DynamoDB

## Monitoring & Maintenance

1. **Monitor logs**: 
   - Heroku: `heroku logs --tail`
   - VPS: `tail -f /var/log/syslog`

2. **Backup data**:
   - For JSON store: regularly backup `data/store.json`
   - Set up automated backups

3. **Performance optimization**:
   - Use a CDN for static files
   - Add caching headers to CSS/JS
   - Consider Redis for session storage

## Security Checklist

- ✅ Environment variables used for secrets
- ✅ DEBUG mode disabled in production
- ✅ HTTPS/SSL enabled
- ✅ Secure cookies enabled
- ✅ Rate limiting implemented
- ✅ Input validation implemented
- ✅ SQL injection not applicable (JSON store)
- ✅ CORS headers set appropriately

## Troubleshooting

- **Port already in use**: `lsof -i :5000`
- **Permission denied**: Check file permissions on `data/` directory
- **Database locked**: JSON store is single-writer; consider queuing for high load
