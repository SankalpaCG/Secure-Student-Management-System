const crypto = require('crypto');

const CSRF_COOKIE = 'XSRF-TOKEN';
const CSRF_HEADER = 'x-xsrf-token';

function issueCsrfCookie(res) {
  const token = crypto.randomBytes(32).toString('hex');
  const isProd = process.env.NODE_ENV === 'production';
  res.cookie(CSRF_COOKIE, token, {
    httpOnly: false,
    sameSite: 'strict',
    secure: isProd,
    maxAge: 12 * 60 * 60 * 1000,
    path: '/'
  });
  return token;
}

function verifyCsrf(req, res, next) {
  if (process.env.SKIP_CSRF === 'true') {
    return next();
  }

  if (!['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
    return next();
  }

  const path = req.path || req.url || '';
  if (path.endsWith('/health') || path.includes('/auth/csrf')) {
    return next();
  }

  const header = req.get(CSRF_HEADER);
  const cookie = req.cookies && req.cookies[CSRF_COOKIE];

  if (!header || !cookie || typeof header !== 'string' || typeof cookie !== 'string') {
    return res.status(403).json({ error: 'CSRF token missing' });
  }

  const a = Buffer.from(header, 'utf8');
  const b = Buffer.from(cookie, 'utf8');
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
    return res.status(403).json({ error: 'CSRF token invalid' });
  }

  return next();
}

module.exports = { issueCsrfCookie, verifyCsrf, CSRF_COOKIE, CSRF_HEADER };
