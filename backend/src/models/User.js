const { DataTypes } = require('sequelize');
const bcrypt = require('bcryptjs');

module.exports = (sequelize) => {
  const User = sequelize.define(
    'User',
    {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
      },
      email: {
        type: DataTypes.STRING(255),
        allowNull: false,
        unique: true,
        validate: { isEmail: true }
      },
      passwordHash: {
        type: DataTypes.STRING(255),
        allowNull: false,
        field: 'password_hash'
      },
      role: {
        type: DataTypes.ENUM('admin', 'teacher', 'student'),
        allowNull: false,
        defaultValue: 'student'
      },
      firstName: {
        type: DataTypes.STRING(120),
        allowNull: false,
        field: 'first_name'
      },
      lastName: {
        type: DataTypes.STRING(120),
        allowNull: false,
        field: 'last_name'
      },
      studentId: {
        type: DataTypes.STRING(64),
        allowNull: true,
        field: 'student_id',
        comment: 'External student identifier when role is student'
      },
      department: {
        type: DataTypes.STRING(120),
        allowNull: true
      },
      isActive: {
        type: DataTypes.BOOLEAN,
        allowNull: false,
        defaultValue: true,
        field: 'is_active'
      },
      totpSecret: {
        type: DataTypes.STRING(255),
        allowNull: true,
        field: 'totp_secret'
      },
      totpEnabled: {
        type: DataTypes.BOOLEAN,
        allowNull: false,
        defaultValue: false,
        field: 'totp_enabled'
      },
      lastLoginAt: {
        type: DataTypes.DATE,
        allowNull: true,
        field: 'last_login_at'
      }
    },
    {
      tableName: 'users',
      defaultScope: {
        attributes: { exclude: ['passwordHash', 'totpSecret'] }
      },
      scopes: {
        withSecrets: {},
        withPassword: {
          attributes: { exclude: ['totpSecret'] }
        }
      }
    }
  );

  User.prototype.comparePassword = function comparePassword(plain) {
    return bcrypt.compare(plain, this.passwordHash);
  };

  User.hashPassword = async function hashPassword(plain) {
    const rounds = Number(process.env.BCRYPT_ROUNDS || 12);
    return bcrypt.hash(plain, rounds);
  };

  return User;
};
