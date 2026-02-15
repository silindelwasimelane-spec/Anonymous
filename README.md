# Anonymous Messages

Simple anonymous messaging platform with user accounts, recipient links, and secure messaging.

## Features

- ✨ Anonymous messaging - send messages without creating an account
- 🔐 Secure user accounts - create accounts to receive messages
- 🔗 Recipient links - share unique links to receive messages
- 🎨 Theme support - dark/light mode
- 📊 Referral system - earn rewards for inviting friends
- ⚡ Rate limiting - protect against spam
- 📱 Responsive design - works on desktop and mobile

## Quick Start (Development)

### Python/Flask Version (Recommended)

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
# Open http://localhost:5000
```

### Node.js Version (Legacy)

```powershell
npm install
npm start
# Open http://localhost:3000
```

## Deployment

For production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

### Quick Deploy to Heroku

```bash
heroku login
heroku create your-app-name
git push heroku main
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### Docker Deployment

```bash
docker build -t anonymous-messages .
docker run -p 5000:5000 -e SECRET_KEY=your-key anonymous-messages
```

## Environment Variables

See `.env.example` for required environment variables:

- `SECRET_KEY`: Flask session secret key (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DEBUG`: Set to `false` in production
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `5000`)
- `SECURE_COOKIES`: Enable secure cookies (default: `true`)

## Project Structure

```
/
├── app.py                 # Flask application
├── py_db.py              # Database layer (JSON-based)
├── requirements.txt      # Python dependencies
├── public/               # Frontend files
│   ├── index.html
│   ├── signup.html
│   ├── login.html
│   ├── account.html
│   ├── send.html
│   ├── app.js
│   ├── nav.js
│   └── styles.css
├── data/                 # Data storage (created automatically)
│   └── store.json
└── DEPLOYMENT.md         # Detailed deployment guide
```

## API Endpoints

### Public
- `POST /api/messages` - Send anonymous message to public feed
- `POST /api/users/<recipient_id>/messages` - Send message to specific user
- `GET /api/messages` - Get public messages feed

### Authentication Required
- `POST /api/signup` - Create new account
- `POST /api/login` - Login to account
- `POST /api/logout` - Logout
- `GET /api/account/messages` - Get messages for logged-in user
- `GET /api/account/info` - Get account information
- `POST /api/account/update-theme` - Update theme preference
- `POST /api/account/change-password` - Change password
- `POST /api/account/delete` - Delete account

## Rate Limiting

- 30 second cooldown between posts per IP
- Max 5 posts per 10 minute window per IP
- Max 200 posts per day per IP

## Security

- Passwords hashed using Werkzeug
- Rate limiting on message posting
- CSRF protection via secure sessions
- XSS protection with HTML escaping
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)

## Database

Currently uses JSON file-based storage (`data/store.json`). For production with high traffic, consider migrating to PostgreSQL or MongoDB.

## License

MIT

## Support

For issues or questions, see the Contact page in the application.
