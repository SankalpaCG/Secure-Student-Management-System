const request = require('supertest');
const app = require('../src/app');

describe('GET /api/v1/health', () => {
  it('returns ok', async () => {
    const res = await request(app).get('/api/v1/health');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });
});
