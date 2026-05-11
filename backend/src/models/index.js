const { buildSequelize } = require('../config/database');
const defineUser = require('./User');
const defineCourse = require('./Course');
const defineEnrollment = require('./Enrollment');

const sequelize = buildSequelize();

const User = defineUser(sequelize);
const Course = defineCourse(sequelize);
const Enrollment = defineEnrollment(sequelize);

User.hasMany(Course, { foreignKey: 'teacherId', as: 'teachingCourses' });
Course.belongsTo(User, { foreignKey: 'teacherId', as: 'teacher' });

User.hasMany(Enrollment, { foreignKey: 'studentId', as: 'enrollments' });
Enrollment.belongsTo(User, { foreignKey: 'studentId', as: 'student' });

Course.hasMany(Enrollment, { foreignKey: 'courseId', as: 'enrollments' });
Enrollment.belongsTo(Course, { foreignKey: 'courseId', as: 'course' });

module.exports = {
  sequelize,
  User,
  Course,
  Enrollment
};
