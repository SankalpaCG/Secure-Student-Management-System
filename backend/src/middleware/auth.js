const { verifyAccessToken } = require('../utils/jwt');
const { User } = require('../models');

async function authenticate(req, res, next) {
  const authHeader = req.headers.authorization;
  let token;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    token = authHeader.slice(7);
  }

  if (!token) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  try {
    const decoded = verifyAccessToken(token);
    const user = await User.findByPk(decoded.sub);
    if (!user || !user.isActive) {
      return res.status(401).json({ error: 'User not found or inactive' });
    }
    req.user = user;
    req.tokenPayload = decoded;
    return next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

module.exports = { authenticate };
