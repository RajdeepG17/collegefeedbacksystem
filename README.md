# College Feedback System

A comprehensive feedback management system for educational institutions, built with Django and React.

## Features

- User Authentication (Students, Faculty, Staff, Admin)
- Feedback Submission and Management
- Department-wise Feedback Tracking
- Category-based Feedback Organization
- Admin Dashboard with Analytics
- File Attachment Support
- Real-time Notifications
- Secure API Endpoints

## Tech Stack

### Backend
- Django
- Django REST Framework
- PostgreSQL
- Redis (Caching)
- JWT Authentication
- Celery (Task Queue)

### Frontend
- React
- Material-UI
- Redux
- Axios
- Chart.js

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL
- Redis
- npm or yarn

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/college-feedback-system.git
cd college-feedback-system
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Update .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Start the development servers:
```bash
# Backend (in root directory)
python manage.py runserver

# Frontend (in frontend directory)
npm start
```

## API Documentation

The API documentation is available at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`
- OpenAPI Schema: `/swagger.json`

## Testing

Run the test suite:
```bash
# Backend tests
python manage.py test

# Frontend tests
cd frontend
npm test
```

## Security Features

- JWT-based Authentication
- Password Strength Validation
- Login Attempt Limiting
- Input Sanitization
- XSS Protection
- CSRF Protection
- Secure File Uploads
- Rate Limiting

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email support@example.com or create an issue in the repository.