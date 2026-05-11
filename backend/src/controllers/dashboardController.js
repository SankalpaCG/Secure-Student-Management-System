const { User, Course, Enrollment, sequelize } = require('../models');
const { fn, col } = require('sequelize');

async function summary(req, res) {
  const role = req.user.role;

  if (role === 'admin') {
    const [userCounts, courseCount, enrollmentTotal] = await Promise.all([
      User.findAll({
        attributes: ['role', [fn('COUNT', col('User.id')), 'count']],
        group: ['role'],
        raw: true
      }),
      Course.count(),
      Enrollment.count()
    ]);

    const byRole = userCounts.reduce((acc, row) => {
      acc[row.role] = Number(row.count);
      return acc;
    }, {});

    return res.json({
      scope: 'admin',
      usersByRole: byRole,
      courses: courseCount,
      enrollments: enrollmentTotal
    });
  }

  if (role === 'teacher') {
    const teaching = await Course.count({ where: { teacherId: req.user.id } });
    const studentsTaught = await Enrollment.count({
      distinct: true,
      col: 'student_id',
      include: [
        {
          model: Course,
          as: 'course',
          attributes: [],
          where: { teacherId: req.user.id }
        }
      ]
    });
    return res.json({
      scope: 'teacher',
      teachingCourses: teaching,
      studentsTaught
    });
  }

  const myCourses = await Enrollment.count({ where: { studentId: req.user.id, status: 'enrolled' } });
  const completed = await Enrollment.count({ where: { studentId: req.user.id, status: 'completed' } });

  return res.json({
    scope: 'student',
    activeEnrollments: myCourses,
    completedCourses: completed
  });
}

async function activity(req, res) {
  if (req.user.role !== 'admin' && req.user.role !== 'teacher') {
    return res.status(403).json({ error: 'Not allowed' });
  }

  if (sequelize.getDialect() === 'sqlite') {
    return res.json({ enrollmentsByMonth: [] });
  }

  const rows = await sequelize.query(
    `SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, COUNT(*) AS count
     FROM enrollments
     WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 11 MONTH)
     GROUP BY DATE_FORMAT(created_at, '%Y-%m')
     ORDER BY month ASC`,
    { type: sequelize.QueryTypes.SELECT }
  );

  return res.json({ enrollmentsByMonth: rows });
}

module.exports = { summary, activity };
