const express = require('express');
const { body, param, query } = require('express-validator');
const { validate } = require('../middleware/validate');
const { asyncHandler } = require('../utils/asyncHandler');
const { authenticate } = require('../middleware/auth');
const { requireRoles } = require('../middleware/rbac');
const userController = require('../controllers/userController');

const router = express.Router();

router.use(authenticate);

router.get(
  '/',
  requireRoles('admin'),
  query('role').optional().isIn(['admin', 'teacher', 'student']),
  query('q').optional().isString().isLength({ max: 120 }),
  validate,
  asyncHandler(userController.listUsers)
);

router.post(
  '/',
  requireRoles('admin'),
  body('email').isEmail().normalizeEmail(),
  body('password').isString().isLength({ min: 10, max: 128 }),
  body('role').isIn(['admin', 'teacher', 'student']),
  body('firstName').isString().isLength({ min: 1, max: 120 }),
  body('lastName').isString().isLength({ min: 1, max: 120 }),
  body('studentId').optional().isString().isLength({ max: 64 }),
  body('department').optional().isString().isLength({ max: 120 }),
  validate,
  asyncHandler(userController.createUser)
);

router.patch(
  '/:id',
  requireRoles('admin', 'teacher'),
  param('id').isUUID(),
  body('firstName').optional().isString().isLength({ min: 1, max: 120 }),
  body('lastName').optional().isString().isLength({ min: 1, max: 120 }),
  body('department').optional().isString().isLength({ max: 120 }),
  body('studentId').optional().isString().isLength({ max: 64 }),
  body('isActive').optional().isBoolean(),
  body('role').optional().isIn(['admin', 'teacher', 'student']),
  validate,
  asyncHandler(async (req, res, next) => {
    if (req.user.role === 'teacher' && req.params.id !== req.user.id) {
      return res.status(403).json({ error: 'Teachers may only update their own profile' });
    }
    return userController.updateUser(req, res, next);
  })
);

module.exports = router;
