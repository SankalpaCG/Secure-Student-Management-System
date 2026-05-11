const express = require('express');
const { body } = require('express-validator');
const { validate } = require('../middleware/validate');
const { asyncHandler } = require('../utils/asyncHandler');
const authController = require('../controllers/authController');
const { authenticate } = require('../middleware/auth');

const router = express.Router();

router.get(
  '/csrf',
  asyncHandler(async (_req, res) => {
    const { issueCsrfCookie } = require('../middleware/csrf');
    issueCsrfCookie(res);
    res.json({ ok: true });
  })
);

router.post(
  '/login',
  body('email').isEmail().normalizeEmail(),
  body('password').isString().isLength({ min: 8, max: 128 }),
  validate,
  asyncHandler(authController.login)
);

router.post(
  '/2fa/verify',
  body('tempToken').isString().isLength({ min: 10 }),
  body('code').isString().isLength({ min: 6, max: 8 }),
  validate,
  asyncHandler(authController.verifyTwoFactor)
);

router.get('/me', authenticate, asyncHandler(authController.me));

router.post(
  '/2fa/setup',
  authenticate,
  asyncHandler(authController.setupTwoFactor)
);

router.post(
  '/2fa/enable',
  authenticate,
  body('code').isString().isLength({ min: 6, max: 8 }),
  validate,
  asyncHandler(authController.enableTwoFactor)
);

router.post(
  '/2fa/disable',
  authenticate,
  body('password').isString().isLength({ min: 8, max: 128 }),
  body('code').isString().isLength({ min: 6, max: 8 }),
  validate,
  asyncHandler(authController.disableTwoFactor)
);

module.exports = router;
