const { User } = require('../models');
const { Op } = require('sequelize');

async function listUsers(req, res) {
  const { role, q } = req.query;
  const where = {};
  if (role) where.role = role;
  if (q) {
    where[Op.or] = [
      { email: { [Op.like]: `%${q}%` } },
      { firstName: { [Op.like]: `%${q}%` } },
      { lastName: { [Op.like]: `%${q}%` } }
    ];
  }

  const users = await User.findAll({
    where,
    order: [['createdAt', 'DESC']],
    limit: 100
  });
  return res.json({ users });
}

async function createUser(req, res) {
  const { email, password, role, firstName, lastName, studentId, department } = req.body;
  const exists = await User.findOne({ where: { email: email.toLowerCase() } });
  if (exists) {
    return res.status(409).json({ error: 'Email already registered' });
  }

  const passwordHash = await User.hashPassword(password);
  const user = await User.create({
    email: email.toLowerCase(),
    passwordHash,
    role,
    firstName,
    lastName,
    studentId: role === 'student' ? studentId : null,
    department: department || null
  });

  return res.status(201).json({ user });
}

async function updateUser(req, res) {
  const { id } = req.params;
  const user = await User.findByPk(id);
  if (!user) return res.status(404).json({ error: 'User not found' });

  const { firstName, lastName, department, studentId, isActive, role } = req.body;
  const updates = {};
  if (firstName !== undefined) updates.firstName = firstName;
  if (lastName !== undefined) updates.lastName = lastName;
  if (department !== undefined) updates.department = department;
  if (studentId !== undefined && user.role === 'student') updates.studentId = studentId;
  if (req.user.role === 'admin') {
    if (isActive !== undefined) updates.isActive = isActive;
    if (role !== undefined) updates.role = role;
  }

  await user.update(updates);
  return res.json({ user });
}

module.exports = { listUsers, createUser, updateUser };
