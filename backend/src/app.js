const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const rateLimit = require('express-rate-limit');

const { sanitizeInput } = require('./middleware/sanitizeInput');
const { verifyCsrf } = require('./middleware/csrf');
const { errorHandler } = require('./middleware/errorHandler');

const authRoutes = require('./routes/authRoutes');
const userRoutes = require('./routes/userRoutes');
const courseRoutes = require('./routes/courseRoutes');
const dashboardRoutes = require('./routes/dashboardRoutes');

const app = express();

const origins = (process.env.FRONTEND_ORIGIN || 'http://localhost:5173')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

app.set('trust proxy', 1);

app.use(
  helmet({
    crossOriginResourcePolicy: { policy: 'cross-origin' }
  })
);

app.use(
  cors({
    origin: origins,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-XSRF-TOKEN', 'X-Requested-With']
  })
);

const globalLimiter = rateLimit({
  windowMs: Number(process.env.RATE_LIMIT_WINDOW_MS || 15 * 60 * 1000),
  max: Number(process.env.RATE_LIMIT_MAX || 400),
  standardHeaders: true,
  legacyHeaders: false
});

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: Number(process.env.AUTH_RATE_LIMIT_MAX || 40),
  standardHeaders: true,
  legacyHeaders: false,
  skipSuccessfulRequests: false
});

app.use(globalLimiter);

const v1 = express.Router();

v1.use(cookieParser());
v1.use(express.json({ limit: '1mb' }));
v1.use(sanitizeInput);
v1.use(verifyCsrf);

v1.get('/health', (_req, res) => {
  res.json({ status: 'ok', service: 'ssms-api' });
});

v1.use('/auth', authLimiter, authRoutes);
v1.use('/users', userRoutes);
v1.use('/courses', courseRoutes);
v1.use('/dashboard', dashboardRoutes);

app.use('/api/v1', v1);

app.use(errorHandler);

module.exports = app;
