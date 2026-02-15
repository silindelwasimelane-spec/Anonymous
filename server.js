const express = require('express');
const path = require('path');
const db = require('./db');
const rateLimit = require('./rateLimiter');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');

// simple in-memory token map: token -> userId
const tokens = new Map();

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/messages', (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 100, 500);
  const messages = db.getMessages(limit);
  res.json(messages);
});

app.post('/api/messages', rateLimit, (req, res) => {
  const { content } = req.body;
  if (!content || typeof content !== 'string') {
    return res.status(400).json({ error: 'Invalid content' });
  }
  const trimmed = content.trim();
  if (trimmed.length === 0 || trimmed.length > 500) {
    return res.status(400).json({ error: 'Content must be 1-500 characters' });
  }
  const id = db.addMessage(trimmed);
  const msg = db.getMessageById(id);
  res.status(201).json(msg);
});

// Create account
app.post('/api/signup', (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) return res.status(400).json({ error: 'username and password required' });
  if (typeof username !== 'string' || typeof password !== 'string') return res.status(400).json({ error: 'invalid input' });
  if (username.length > 32 || password.length > 128) return res.status(400).json({ error: 'input too long' });
  const existing = db.getUserByUsername(username);
  if (existing) return res.status(409).json({ error: 'username taken' });
  const passwordHash = bcrypt.hashSync(password, 10);
  const recipientId = crypto.randomBytes(6).toString('hex');
  const user = db.createUser(username, passwordHash, recipientId);
  const token = crypto.randomBytes(24).toString('hex');
  tokens.set(token, user.id);
  res.status(201).json({ message: 'account created', recipientLink: `/u/${recipientId}`, token });
});

// Login
app.post('/api/login', (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) return res.status(400).json({ error: 'username and password required' });
  const user = db.getUserByUsername(username);
  if (!user) return res.status(401).json({ error: 'invalid credentials' });
  if (!bcrypt.compareSync(password, user.passwordHash)) return res.status(401).json({ error: 'invalid credentials' });
  const token = crypto.randomBytes(24).toString('hex');
  tokens.set(token, user.id);
  res.json({ token, recipientLink: `/u/${user.recipientId}` });
});

// Get account messages (requires token)
app.get('/api/account/messages', (req, res) => {
  const auth = req.get('authorization') || '';
  const [, token] = auth.split(' ') || [];
  if (!token || !tokens.has(token)) return res.status(401).json({ error: 'unauthorized' });
  const userId = tokens.get(token);
  const messages = db.getMessagesForUserId(userId, 500);
  res.json(messages);
});

// Public send to user by recipientId
app.post('/api/users/:recipientId/messages', rateLimit, (req, res) => {
  const { recipientId } = req.params;
  const { content } = req.body || {};
  if (!content || typeof content !== 'string') return res.status(400).json({ error: 'Invalid content' });
  const trimmed = content.trim();
  if (trimmed.length === 0 || trimmed.length > 500) return res.status(400).json({ error: 'Content must be 1-500 characters' });
  const id = db.addMessageToUserByRecipient(recipientId, trimmed);
  if (!id) return res.status(404).json({ error: 'recipient not found' });
  res.status(201).json({ id });
});

// Serve the public send page for /u/:recipientId
app.get('/u/:recipientId', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'send.html'));
});

// Serve account page
app.get('/account', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'account.html'));
});

// Serve signup and login pages
app.get('/signup', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'signup.html'));
});

app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server listening on http://localhost:${port}`));
