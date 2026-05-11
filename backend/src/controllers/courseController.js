const { Course, User, Enrollment } = require('../models');

async function listCourses(req, res) {
  const where = {};
  if (req.user.role === 'teacher') {
    where.teacherId = req.user.id;
  }
  // Students and admins see all courses (students need catalog to enroll)

  const courses = await Course.findAll({
    where,
    include: [{ model: User, as: 'teacher', attributes: ['id', 'firstName', 'lastName', 'email'] }],
    order: [['created_at', 'DESC']]
  });
  return res.json({ courses });
}

async function createCourse(req, res) {
  const { code, name, description, credits, teacherId } = req.body;
  let teacher = req.user.id;
  if (req.user.role === 'admin' && teacherId) {
    teacher = teacherId;
  }

  const course = await Course.create({
    code,
    name,
    description,
    credits: credits ?? 3,
    teacherId: teacher
  });

  const full = await Course.findByPk(course.id, {
    include: [{ model: User, as: 'teacher', attributes: ['id', 'firstName', 'lastName', 'email'] }]
  });
  return res.status(201).json({ course: full });
}

async function updateCourse(req, res) {
  const course = await Course.findByPk(req.params.id);
  if (!course) return res.status(404).json({ error: 'Course not found' });
  if (req.user.role === 'teacher' && course.teacherId !== req.user.id) {
    return res.status(403).json({ error: 'Not allowed' });
  }

  const { name, description, credits } = req.body;
  await course.update({
    ...(name !== undefined ? { name } : {}),
    ...(description !== undefined ? { description } : {}),
    ...(credits !== undefined ? { credits } : {})
  });
  return res.json({ course });
}

async function deleteCourse(req, res) {
  const course = await Course.findByPk(req.params.id);
  if (!course) return res.status(404).json({ error: 'Course not found' });
  if (req.user.role === 'teacher' && course.teacherId !== req.user.id) {
    return res.status(403).json({ error: 'Not allowed' });
  }
  await course.destroy();
  return res.status(204).send();
}

async function enroll(req, res) {
  const course = await Course.findByPk(req.params.id);
  if (!course) return res.status(404).json({ error: 'Course not found' });
  if (req.user.role !== 'student') {
    return res.status(403).json({ error: 'Only students can self-enroll' });
  }

  const [row, created] = await Enrollment.findOrCreate({
    where: { courseId: course.id, studentId: req.user.id },
    defaults: { status: 'enrolled' }
  });

  if (!created && row.status === 'dropped') {
    await row.update({ status: 'enrolled' });
  }

  return res.status(created ? 201 : 200).json({ enrollment: row });
}

async function listEnrollments(req, res) {
  const course = await Course.findByPk(req.params.id);
  if (!course) return res.status(404).json({ error: 'Course not found' });
  if (req.user.role === 'teacher' && course.teacherId !== req.user.id) {
    return res.status(403).json({ error: 'Not allowed' });
  }
  if (req.user.role === 'admin' || req.user.role === 'teacher') {
    const rows = await Enrollment.findAll({
      where: { courseId: course.id },
      include: [{ model: User, as: 'student', attributes: ['id', 'email', 'firstName', 'lastName', 'studentId'] }]
    });
    return res.json({ enrollments: rows });
  }
  return res.status(403).json({ error: 'Not allowed' });
}

async function updateGrade(req, res) {
  const { enrollmentId } = req.params;
  const { grade } = req.body;
  const enrollment = await Enrollment.findByPk(enrollmentId, { include: [{ model: Course, as: 'course' }] });
  if (!enrollment) return res.status(404).json({ error: 'Enrollment not found' });
  const course = enrollment.course;
  if (req.user.role === 'teacher' && course.teacherId !== req.user.id) {
    return res.status(403).json({ error: 'Not allowed' });
  }
  await enrollment.update({ grade });
  return res.json({ enrollment });
}

module.exports = {
  listCourses,
  createCourse,
  updateCourse,
  deleteCourse,
  enroll,
  listEnrollments,
  updateGrade
};
