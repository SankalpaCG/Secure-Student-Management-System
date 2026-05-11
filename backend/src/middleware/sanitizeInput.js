const sanitizeHtml = require('sanitize-html');
const validator = require('validator');

function sanitizeString(value) {
  if (typeof value !== 'string') return value;
  const trimmed = value.trim();
  const noHtml = sanitizeHtml(trimmed, { allowedTags: [], allowedAttributes: {} });
  return validator.escape(noHtml);
}

function walkAndSanitize(obj) {
  if (obj === null || obj === undefined) return obj;
  if (Array.isArray(obj)) {
    return obj.map((item) => walkAndSanitize(item));
  }
  if (typeof obj === 'object' && !(obj instanceof Date) && !Buffer.isBuffer(obj)) {
    const out = {};
    for (const key of Object.keys(obj)) {
      out[key] = walkAndSanitize(obj[key]);
    }
    return out;
  }
  if (typeof obj === 'string') {
    return sanitizeString(obj);
  }
  return obj;
}

/**
 * Sanitizes string fields in JSON body (HTML stripped, entities escaped).
 * Skips raw binary and preserves numbers/booleans.
 */
function sanitizeInput(req, _res, next) {
  if (req.body && typeof req.body === 'object') {
    req.body = walkAndSanitize(req.body);
  }
  next();
}

module.exports = { sanitizeInput, sanitizeString };
