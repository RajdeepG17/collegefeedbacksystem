import { rest } from 'msw';

const mockUsers = [
  {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    role: 'user'
  },
  {
    id: 2,
    username: 'admin',
    email: 'admin@example.com',
    role: 'admin'
  }
];

const mockFeedbacks = [
  {
    id: 1,
    title: 'Test Feedback',
    description: 'This is a test feedback',
    category: 'academic',
    status: 'pending',
    priority: 'medium',
    submitter: 1,
    created_at: '2024-01-01T00:00:00Z'
  }
];

export const handlers = [
  // Auth endpoints
  rest.post('/api/auth/login/', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
      })
    );
  }),

  rest.post('/api/auth/register/', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 3,
        email: req.body.email,
        username: req.body.username,
        role: 'user'
      })
    );
  }),

  // Feedback endpoints
  rest.get('/api/feedback/', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          title: 'Test Feedback',
          content: 'Test Content',
          status: 'PENDING',
        },
      ])
    );
  }),

  rest.post('/api/feedback/feedbacks/', (req, res, ctx) => {
    const newFeedback = {
      id: mockFeedbacks.length + 1,
      ...req.body,
      created_at: new Date().toISOString(),
      status: 'pending'
    };
    mockFeedbacks.push(newFeedback);
    return res(ctx.status(201), ctx.json(newFeedback));
  }),

  rest.get('/api/feedback/feedbacks/', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockFeedbacks));
  }),

  // Notifications
  rest.get('/api/notifications/', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          message: 'New feedback submitted',
          is_read: false,
          created_at: new Date().toISOString()
        }
      ])
    );
  }),

  // Error handling
  rest.get('*', (req, res, ctx) => {
    console.error(`Unhandled request: ${req.url.toString()}`);
    return res(ctx.status(500));
  }),
]; 