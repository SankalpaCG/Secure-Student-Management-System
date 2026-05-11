const express = require('express');
const { asyncHandler } = require('../utils/asyncHandler');
const { authenticate } = require('../middleware/auth');
const dashboardController = require('../controllers/dashboardController');

const router = express.Router();

router.use(authenticate);

router.get('/summary', asyncHandler(dashboardController.summary));
router.get('/activity', asyncHandler(dashboardController.activity));

module.exports = router;
