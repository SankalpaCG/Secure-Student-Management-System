const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  return sequelize.define(
    'Enrollment',
    {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
      },
      courseId: {
        type: DataTypes.UUID,
        allowNull: false,
        field: 'course_id',
        references: { model: 'courses', key: 'id' }
      },
      studentId: {
        type: DataTypes.UUID,
        allowNull: false,
        field: 'student_id',
        references: { model: 'users', key: 'id' }
      },
      status: {
        type: DataTypes.ENUM('enrolled', 'completed', 'dropped'),
        allowNull: false,
        defaultValue: 'enrolled'
      },
      grade: {
        type: DataTypes.DECIMAL(5, 2),
        allowNull: true
      }
    },
    {
      tableName: 'enrollments',
      indexes: [
        { unique: true, fields: ['course_id', 'student_id'] }
      ]
    }
  );
};
