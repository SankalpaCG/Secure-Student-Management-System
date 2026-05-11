require('dotenv').config();
const app = require('./app');
const { sequelize } = require('./models');

const PORT = Number(process.env.PORT || 4000);

async function start() {
  await sequelize.authenticate();
  if (process.env.NODE_ENV !== 'production') {
    await sequelize.sync();
  }
  app.listen(PORT, () => {
    // eslint-disable-next-line no-console
    console.log(`SSMS API listening on http://localhost:${PORT}`);
  });
}

start().catch((err) => {
  // eslint-disable-next-line no-console
  console.error('Failed to start server', err);
  process.exit(1);
});
