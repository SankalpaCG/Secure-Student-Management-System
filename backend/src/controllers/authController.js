const { User } = require('../models');
const { signAccessToken, signTempToken, verifyTempToken } = require('../utils/jwt');
const { generateSecret, verifyCode, qrDataUrl } = require('../services/totpService');

async function login(req, res) {
  const { email, password } = req.body;
  const user = await User.unscoped().findOne({ where: { email: email.toLowerCase() } });
  if (!user || !(await user.comparePassword(password))) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  if (!user.isActive) {
    return res.status(403).json({ error: 'Account disabled' });
  }

  await user.update({ lastLoginAt: new Date() });

  if (user.totpEnabled && user.totpSecret) {
    const tempToken = signTempToken(user.id);
    return res.json({
      requiresTwoFactor: true,
      tempToken,
      user: { id: user.id, email: user.email, role: user.role, firstName: user.firstName, lastName: user.lastName }
    });
  }

  const accessToken = signAccessToken({
    sub: user.id,
    role: user.role,
    email: user.email
  });

  return res.json({
    requiresTwoFactor: false,
    accessToken,
    user: { id: user.id, email: user.email, role: user.role, firstName: user.firstName, lastName: user.lastName }
  });
}

async function verifyTwoFactor(req, res) {
  const { tempToken, code } = req.body;
  let payload;
  try {
    payload = verifyTempToken(tempToken);
  } catch {
    return res.status(401).json({ error: 'Invalid or expired temporary token' });
  }

  const user = await User.unscoped().findByPk(payload.sub);
  if (!user || !user.totpEnabled || !user.totpSecret) {
    return res.status(400).json({ error: 'Two-factor authentication is not active for this account' });
  }

  if (!verifyCode(user.totpSecret, code)) {
    return res.status(401).json({ error: 'Invalid authenticator code' });
  }

  const accessToken = signAccessToken({
    sub: user.id,
    role: user.role,
    email: user.email
  });

  return res.json({
    accessToken,
    user: { id: user.id, email: user.email, role: user.role, firstName: user.firstName, lastName: user.lastName }
  });
}

async function me(req, res) {
  const user = await User.findByPk(req.user.id);
  return res.json({ user });
}

async function setupTwoFactor(req, res) {
  const user = await User.unscoped().findByPk(req.user.id);
  if (user.totpEnabled) {
    return res.status(400).json({ error: 'Two-factor authentication is already enabled' });
  }

  const secret = generateSecret(user.email);
  await user.update({ totpSecret: secret.base32, totpEnabled: false });

  const qr = await qrDataUrl(secret.otpauth_url);
  return res.json({
    otpauthUrl: secret.otpauth_url,
    qrDataUrl: qr,
    message: 'Scan the QR code, then confirm with a valid code using POST /auth/2fa/enable'
  });
}

async function enableTwoFactor(req, res) {
  const { code } = req.body;
  const user = await User.unscoped().findByPk(req.user.id);
  if (!user.totpSecret) {
    return res.status(400).json({ error: 'Run setup first' });
  }
  if (user.totpEnabled) {
    return res.status(400).json({ error: 'Already enabled' });
  }
  if (!verifyCode(user.totpSecret, code)) {
    return res.status(400).json({ error: 'Invalid authenticator code' });
  }
  await user.update({ totpEnabled: true });
  const fresh = await User.findByPk(user.id);
  return res.json({ user: fresh, message: 'Two-factor authentication enabled' });
}

async function disableTwoFactor(req, res) {
  const { password, code } = req.body;
  const user = await User.unscoped().findByPk(req.user.id);
  if (!user.totpEnabled) {
    return res.status(400).json({ error: 'Two-factor authentication is not enabled' });
  }
  if (!(await user.comparePassword(password))) {
    return res.status(401).json({ error: 'Invalid password' });
  }
  if (!verifyCode(user.totpSecret, code)) {
    return res.status(401).json({ error: 'Invalid authenticator code' });
  }
  await user.update({ totpEnabled: false, totpSecret: null });
  const fresh = await User.findByPk(user.id);
  return res.json({ user: fresh, message: 'Two-factor authentication disabled' });
}

module.exports = {
  login,
  verifyTwoFactor,
  me,
  setupTwoFactor,
  enableTwoFactor,
  disableTwoFactor
};
