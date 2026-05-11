require('dotenv').config();
const { sequelize } = require('../models');

async function migrate() {
  await sequelize.authenticate();
  await sequelize.sync();
  // eslint-disable-next-line no-console
  console.log('Database schema synchronized.');
  await sequelize.close();
}

migrate().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});
