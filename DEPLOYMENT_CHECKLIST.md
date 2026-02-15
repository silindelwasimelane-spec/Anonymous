# Pre-Deployment Checklist

Follow this checklist before deploying to production:

## Code & Configuration
- [ ] **Update `.env` file** with production values:
  - [ ] Generate a strong `SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(32))"`
  - [ ] Set `DEBUG=false`
  - [ ] Set `SECURE_COOKIES=true`
  - [ ] Update `HOST` and `PORT` as needed for your platform
  
- [ ] **Review security settings** in `app.py`:
  - [ ] Security headers are enabled (CORS, X-Frame-Options, etc.)
  - [ ] HTTPS is enforced in production
  - [ ] Session cookies are HttpOnly and Secure

## Dependencies
- [ ] **All dependencies installed**: `pip install -r requirements.txt`
- [ ] **For Heroku/cloud platforms**: Add `gunicorn` to requirements:
  ```bash
  pip install gunicorn
  pip freeze > requirements.txt
  ```

## Database
- [ ] **Backup existing data** if migrating: Copy `data/store.json`
- [ ] **Data directory writable**: Ensure `data/` directory has proper permissions
- [ ] **For production**: Consider migrating from JSON to PostgreSQL/MongoDB

## Frontend
- [ ] **Test all pages**:
  - [ ] Index / home page
  - [ ] Signup and login
  - [ ] Account page and settings
  - [ ] Message sending
  - [ ] Responsive design on mobile
  
- [ ] **Check that links don't reference localhost**:
  - [ ] All API calls use relative paths (e.g., `/api/...`)
  - [ ] No hardcoded localhost references

## Platform-Specific

### Heroku
- [ ] **Create Procfile** (included)
- [ ] **Create runtime.txt** (included)
- [ ] **Push to Heroku**:
  ```bash
  heroku login
  heroku create your-app-name
  git push heroku main
  ```
- [ ] **Set environment variables**:
  ```bash
  heroku config:set SECRET_KEY=<your-secret>
  heroku config:set DEBUG=false
  ```

### Docker/Container
- [ ] **Docker image builds**: `docker build -t app .`
- [ ] **Environment variables passed correctly**
- [ ] **Port mapping correct**: Default 5000

### VPS/Self-hosted
- [ ] **Python 3.9+ installed**
- [ ] **Virtual environment created**
- [ ] **systemd service created and enabled**
- [ ] **Nginx reverse proxy configured**
- [ ] **SSL certificate installed** (Let's Encrypt)
- [ ] **Firewall rules configured**

## Testing
- [ ] **App starts without errors**: `python app.py`
- [ ] **API endpoints respond**:
  - [ ] `GET /` → 200 OK
  - [ ] `GET /api/signup` → Should serve signup page
  - [ ] `POST /api/signup` → Should create user (test with curl/Postman)
  
- [ ] **Database operations work**:
  - [ ] Users can sign up
  - [ ] Users can log in
  - [ ] Messages can be sent
  - [ ] Messages appear in inbox

- [ ] **Rate limiting works**:
  - [ ] Rapid requests are throttled
  - [ ] Proper error responses

## Performance & Monitoring
- [ ] **Set up logging**: Monitor `/var/log/` or platform logs
- [ ] **Monitor uptime**: Set up health checks
- [ ] **Performance tested**: App responds quickly under load
- [ ] **Database backups scheduled**: Automated backup of `data/store.json` or database

## Post-Deployment
- [ ] **Health check enabled**: App responds to `GET /`
- [ ] **Error handling**: Check logs for any errors
- [ ] **Users can access**: Share the URL with test users
- [ ] **Monitoring alerts set up**: Be notified of issues
- [ ] **Document deployment**: Keep notes for future reference

## Common Issues & Fixes

### Port Already in Use
```bash
# Find process using port
lsof -i :5000

# Kill process (if needed)
kill -9 <PID>
```

### Permission Denied on `data/` directory
```bash
chmod 755 data/
chmod 644 data/*.json
```

### SECRET_KEY Not Set
```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### Database Locked (JSON file too large)
- Consider migrating to PostgreSQL
- Or implement connection pooling for concurrent access

## Useful Commands

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Test app locally before deploying:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```

**Deploy to Heroku:**
```bash
heroku login
heroku create your-app-name
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set SECRET_KEY=$SECRET_KEY
git push heroku main
```

## Support
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed platform-specific instructions
- Check application logs for errors
- Review [README.md](README.md) for API documentation
