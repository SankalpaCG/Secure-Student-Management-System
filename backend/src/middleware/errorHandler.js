// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
  const status = err.status || err.statusCode || 500;
  const message = err.message || 'Internal Server Error';
  if (process.env.NODE_ENV === 'development') {
    // eslint-disable-next-line no-console
    console.error(err);
  }
  res.status(status).json({
    error: message,
    ...(process.env.NODE_ENV === 'development' && err.stack ? { stack: err.stack } : {})
  });
}

module.exports = { errorHandler };
