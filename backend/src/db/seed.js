require('dotenv').config();
const { sequelize, User, Course, Enrollment } = require('../models');

async function seed() {
  await sequelize.sync();

  const password = 'ChangeMe!1';

  const [admin, teacher, student] = await Promise.all([
    User.findOrCreate({
      where: { email: 'admin@ssms.local' },
      defaults: {
        passwordHash: await User.hashPassword(password),
        role: 'admin',
        firstName: 'Alex',
        lastName: 'Admin',
        isActive: true
      }
    }),
    User.findOrCreate({
      where: { email: 'teacher@ssms.local' },
      defaults: {
        passwordHash: await User.hashPassword(password),
        role: 'teacher',
        firstName: 'Taylor',
        lastName: 'Teacher',
        department: 'Computer Science',
        isActive: true
      }
    }),
    User.findOrCreate({
      where: { email: 'student@ssms.local' },
      defaults: {
        passwordHash: await User.hashPassword(password),
        role: 'student',
        firstName: 'Sam',
        lastName: 'Student',
        studentId: 'STU-1001',
        department: 'Computer Science',
        isActive: true
      }
    })
  ]);

  const adminUser = admin[0];
  const teacherUser = teacher[0];
  const studentUser = student[0];

  if (admin[1]) await adminUser.update({ passwordHash: await User.hashPassword(password) });
  if (teacher[1]) await teacherUser.update({ passwordHash: await User.hashPassword(password) });
  if (student[1]) await studentUser.update({ passwordHash: await User.hashPassword(password) });

  const [c1] = await Course.findOrCreate({
    where: { code: 'CS101' },
    defaults: {
      name: 'Introduction to Programming',
      description: 'Foundational programming concepts and problem solving.',
      credits: 4,
      teacherId: teacherUser.id
    }
  });

  const [c2] = await Course.findOrCreate({
    where: { code: 'CS201' },
    defaults: {
      name: 'Data Structures',
      description: 'Lists, trees, graphs, and algorithmic analysis.',
      credits: 4,
      teacherId: teacherUser.id
    }
  });

  await Enrollment.findOrCreate({
    where: { courseId: c1.id, studentId: studentUser.id },
    defaults: { status: 'enrolled', grade: 88.5 }
  });

  await Enrollment.findOrCreate({
    where: { courseId: c2.id, studentId: studentUser.id },
    defaults: { status: 'enrolled', grade: null }
  });

  // eslint-disable-next-line no-console
  console.log('Seed completed: demo users and courses are ready.');
  await sequelize.close();
}

seed().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});
