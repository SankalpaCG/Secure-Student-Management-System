process.env.NODE_ENV = 'test';
process.env.USE_SQLITE = 'true';
process.env.JWT_SECRET = 'unit-test-jwt-secret-do-not-use-in-production-32chars';
process.env.SKIP_CSRF = 'true';
process.env.FRONTEND_ORIGIN = 'http://localhost:5173';
