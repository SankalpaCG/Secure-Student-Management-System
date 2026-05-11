function requireRoles(...allowedRoles) {
  const set = new Set(allowedRoles.flat());
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    if (!set.has(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    return next();
  };
}

module.exports = { requireRoles };
