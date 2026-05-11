const request = require('supertest');
const { sequelize, User } = require('../src/models');
const app = require('../src/app');

describe('Auth API', () => {
  beforeAll(async () => {
    await sequelize.sync({ force: true });
    await User.create({
      email: 'teacher@test.local',
      passwordHash: await User.hashPassword('Password123!'),
      role: 'teacher',
      firstName: 'T',
      lastName: 'T',
      isActive: true
    });
  });

  it('rejects invalid login', async () => {
    const res = await request(app).post('/api/v1/auth/login').send({
      email: 'teacher@test.local',
      password: 'wrong-password'
    });
    expect(res.status).toBe(401);
  });

  it('logs in with valid credentials', async () => {
    const res = await request(app).post('/api/v1/auth/login').send({
      email: 'teacher@test.local',
      password: 'Password123!'
    });
    expect(res.status).toBe(200);
    expect(res.body.accessToken).toBeDefined();
    expect(res.body.user.role).toBe('teacher');
  });
});
