const jwt = require('jsonwebtoken');

function signAccessToken(payload) {
  const secret = process.env.JWT_SECRET;
  if (!secret || (process.env.NODE_ENV === 'production' && secret.length < 32)) {
    throw new Error('JWT_SECRET must be set and at least 32 characters in production');
  }
  const expiresIn = process.env.JWT_EXPIRES_IN || '15m';
  return jwt.sign(payload, secret, { expiresIn, issuer: 'ssms', audience: 'ssms-clients' });
}

function verifyAccessToken(token) {
  const secret = process.env.JWT_SECRET;
  return jwt.verify(token, secret, { issuer: 'ssms', audience: 'ssms-clients' });
}

function signTempToken(userId) {
  const secret = process.env.JWT_SECRET;
  return jwt.sign({ sub: userId, typ: '2fa_pending' }, secret, {
    expiresIn: '5m',
    issuer: 'ssms',
    audience: 'ssms-2fa'
  });
}

function verifyTempToken(token) {
  const secret = process.env.JWT_SECRET;
  return jwt.verify(token, secret, { issuer: 'ssms', audience: 'ssms-2fa' });
}

module.exports = { signAccessToken, verifyAccessToken, signTempToken, verifyTempToken };
