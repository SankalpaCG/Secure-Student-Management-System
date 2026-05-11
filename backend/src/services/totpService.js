const speakeasy = require('speakeasy');
const QRCode = require('qrcode');

function generateSecret(email) {
  return speakeasy.generateSecret({
    name: `SSMS (${email})`,
    issuer: 'Secure Student Management System',
    length: 32
  });
}

function verifyCode(secretBase32, token) {
  return speakeasy.totp.verify({
    secret: secretBase32,
    encoding: 'base32',
    token: String(token).replace(/\s/g, ''),
    window: 1
  });
}

async function qrDataUrl(otpauthUrl) {
  return QRCode.toDataURL(otpauthUrl);
}

module.exports = { generateSecret, verifyCode, qrDataUrl };
