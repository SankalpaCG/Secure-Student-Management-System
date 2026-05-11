const express = require('express');
const { body, param } = require('express-validator');
const { validate } = require('../middleware/validate');
const { asyncHandler } = require('../utils/asyncHandler');
const { authenticate } = require('../middleware/auth');
const { requireRoles } = require('../middleware/rbac');
const courseController = require('../controllers/courseController');

const router = express.Router();

router.use(authenticate);

router.get('/', asyncHandler(courseController.listCourses));

router.post(
  '/',
  requireRoles('admin', 'teacher'),
  body('code').isString().isLength({ min: 2, max: 32 }),
  body('name').isString().isLength({ min: 2, max: 255 }),
  body('description').optional().isString().isLength({ max: 4000 }),
  body('credits').optional().isInt({ min: 1, max: 12 }),
  body('teacherId').optional().isUUID(),
  validate,
  asyncHandler(courseController.createCourse)
);

router.patch(
  '/:id',
  requireRoles('admin', 'teacher'),
  param('id').isUUID(),
  body('name').optional().isString().isLength({ min: 2, max: 255 }),
  body('description').optional().isString().isLength({ max: 4000 }),
  body('credits').optional().isInt({ min: 1, max: 12 }),
  validate,
  asyncHandler(courseController.updateCourse)
);

router.delete(
  '/:id',
  requireRoles('admin', 'teacher'),
  param('id').isUUID(),
  validate,
  asyncHandler(courseController.deleteCourse)
);

router.post(
  '/:id/enroll',
  requireRoles('student'),
  param('id').isUUID(),
  validate,
  asyncHandler(courseController.enroll)
);

router.get(
  '/:id/enrollments',
  requireRoles('admin', 'teacher'),
  param('id').isUUID(),
  validate,
  asyncHandler(courseController.listEnrollments)
);

router.patch(
  '/enrollments/:enrollmentId/grade',
  requireRoles('admin', 'teacher'),
  param('enrollmentId').isUUID(),
  body('grade').isFloat({ min: 0, max: 100 }),
  validate,
  asyncHandler(courseController.updateGrade)
);

module.exports = router;
