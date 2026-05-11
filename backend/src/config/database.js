const { Sequelize } = require('sequelize');

function buildSequelize() {
  if (process.env.NODE_ENV === 'test' && process.env.USE_SQLITE === 'true') {
    return new Sequelize({
      dialect: 'sqlite',
      storage: ':memory:',
      logging: false,
      define: {
        underscored: true,
        timestamps: true
      }
    });
  }

  const url = process.env.DATABASE_URL;
  if (url) {
    return new Sequelize(url, {
      dialect: 'mysql',
      logging: process.env.NODE_ENV === 'development' ? console.log : false,
      define: {
        underscored: true,
        timestamps: true
      }
    });
  }

  return new Sequelize(
    process.env.DB_NAME || 'ssms',
    process.env.DB_USER || 'ssms_user',
    process.env.DB_PASSWORD || 'ssms_password',
    {
      host: process.env.DB_HOST || '127.0.0.1',
      port: Number(process.env.DB_PORT || 3306),
      dialect: 'mysql',
      logging: process.env.NODE_ENV === 'development' ? console.log : false,
      define: {
        underscored: true,
        timestamps: true
      }
    }
  );
}

module.exports = { buildSequelize };
