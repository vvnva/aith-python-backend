import http from 'k6/http';

const baseUrl = 'http://localhost:8000';

export const options = {
  scenarios: {
    constant_request_rate: {
      executor: 'ramping-arrival-rate',
      startRate: 0,
      stages: [
        { target: 60000, duration: '10m' },
      ],
      preAllocatedVUs: 100,
      maxVUs: 100,
    },
  },
};

export default function () {
  const url = 'http://localhost:8000/user-register';
  const payload = JSON.stringify({
    username: `testuser_${__VU}_${__ITER}`,
    name: 'Test User',
    birthdate: '2000-01-01T00:00:00Z',
    password: 'password123',
  });

  const params = {headers: {'Content-Type': 'application/json',},};

  const res = http.post(url, payload, params);}
