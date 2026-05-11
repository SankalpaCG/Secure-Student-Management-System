const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  return sequelize.define(
    'Course',
    {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
      },
      code: {
        type: DataTypes.STRING(32),
        allowNull: false,
        unique: true
      },
      name: {
        type: DataTypes.STRING(255),
        allowNull: false
      },
      description: {
        type: DataTypes.TEXT,
        allowNull: true
      },
      credits: {
        type: DataTypes.INTEGER,
        allowNull: false,
        defaultValue: 3
      },
      teacherId: {
        type: DataTypes.UUID,
        allowNull: false,
        field: 'teacher_id',
        references: { model: 'users', key: 'id' }
      }
    },
    { tableName: 'courses' }
  );
};
