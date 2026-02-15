// Simple in-memory rate limiter for POST /api/messages
// Rules:
// - cooldown: 30s between posts per IP
// - window: 10 minutes, max 5 posts per window per IP
// - daily limit: 200 posts per IP

const WINDOW_MS = 10 * 60 * 1000; // 10 minutes
const WINDOW_LIMIT = 5;
const COOLDOWN_MS = 30 * 1000; // 30 seconds
const DAILY_LIMIT = 200;

const store = new Map();

function todayKey(ts = Date.now()) {
  const d = new Date(ts);
  return d.toISOString().slice(0, 10);
}

function getState(ip) {
  let s = store.get(ip);
  if (!s) {
    s = { posts: [], last: 0, day: todayKey(), dayCount: 0 };
    store.set(ip, s);
  }
  // rotate day
  const t = todayKey();
  if (s.day !== t) {
    s.day = t;
    s.dayCount = 0;
  }
  return s;
}

function rateLimitMiddleware(req, res, next) {
  if (req.method !== 'POST' || !req.path.startsWith('/api/messages')) return next();
  const ip = req.ip || req.connection.remoteAddress || 'unknown';
  const now = Date.now();
  const s = getState(ip);

  // cooldown check
  if (s.last && now - s.last < COOLDOWN_MS) {
    const retry = Math.ceil((COOLDOWN_MS - (now - s.last)) / 1000);
    res.set('Retry-After', String(retry));
    return res.status(429).json({ error: 'Slow down', retryAfter: retry });
  }

  // sliding window check
  s.posts = s.posts.filter(t => t > now - WINDOW_MS);
  if (s.posts.length >= WINDOW_LIMIT) {
    const retryMs = Math.ceil((s.posts[0] + WINDOW_MS - now) / 1000);
    res.set('Retry-After', String(retryMs));
    return res.status(429).json({ error: 'Rate limit exceeded', retryAfter: retryMs });
  }

  // daily limit
  if (s.dayCount >= DAILY_LIMIT) {
    return res.status(429).json({ error: 'Daily limit exceeded' });
  }

  // allow: record
  s.posts.push(now);
  s.last = now;
  s.dayCount += 1;

  // attach rate info headers
  res.set('X-RateLimit-Limit', String(WINDOW_LIMIT));
  res.set('X-RateLimit-Remaining', String(Math.max(0, WINDOW_LIMIT - s.posts.length)));
  res.set('X-RateLimit-Reset', String(Math.ceil((s.posts[0] + WINDOW_MS - now) / 1000)));

  next();
}

module.exports = rateLimitMiddleware;
