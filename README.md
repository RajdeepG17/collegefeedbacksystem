# College Feedback System

A comprehensive feedback management system for educational institutions, built with Django and React. This application enables students, faculty, and staff to submit, track, and manage feedback across various college departments.

## Features

- **User Authentication & Authorization**
  - Role-based access (Students, Faculty, Staff, Admin)
  - JWT Authentication
  - Secure password handling with Argon2
  - User profiles with department association

- **Feedback Management**
  - Submission with optional anonymity
  - Department-wise tracking
  - Category-based organization
  - Status tracking and resolution workflow
  - Priority levels (Low, Medium, High, Critical)
  - File attachment support

- **Dashboard & Analytics**
  - Admin dashboard with feedback insights
  - Department performance metrics
  - Resolution time statistics
  - Category distribution charts

- **Notification System**
  - Real-time updates on feedback status changes
  - Email notifications for administrators
  - User notification center

- **Security Features**
  - JWT token authentication
  - CORS protection
  - Input validation and sanitization
  - Secure file uploads

## Tech Stack

### Backend
- **Django 4.2.7** - Python web framework
- **Django REST Framework 3.14.0** - API development toolkit
- **JWT Authentication** - Token-based authentication
- **SQLite** (Development) - Database
- **Argon2** - Password hashing
- **Django CORS Headers** - Cross-origin resource sharing
- **Structured Logging** - Logging system

### Frontend
- **React 18.2** - JavaScript library for UI
- **Material-UI 5.15** - React UI framework
- **React Router 6.22** - Navigation
- **Axios** - HTTP client
- **Formik & Yup** - Form handling and validation
- **TypeScript** - Type safety

## Project Structure

```
college-feedback-system/
├── accounts/               # User account management app
│   ├── models.py           # User, Department, UserProfile models
│   ├── views.py            # User account views
│   └── serializers.py      # User serializers
│
├── authentication/         # Authentication app
│   ├── views.py            # Auth views (login, logout, etc.)
│   └── serializers.py      # Auth serializers
│
├── feedback/               # Feedback management app
│   ├── models.py           # Feedback, Category, Comment models
│   ├── views.py            # Feedback endpoints
│   ├── serializers.py      # Feedback serializers
│   └── services.py         # Business logic
│
├── college_feedback_system/  # Main Django project
│   ├── settings.py         # Project settings
│   ├── urls.py             # URL declarations
│   └── middleware/         # Custom middleware
│
├── frontend/               # React frontend
│   ├── public/             # Static files
│   └── src/                # Source code
│       ├── components/     # React components
│       ├── pages/          # Page components
│       ├── contexts/       # React contexts
│       ├── services/       # API services
│       ├── utils/          # Utility functions
│       └── hooks/          # Custom React hooks
│
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── functional/         # Functional tests
│
├── utils/                  # Utility scripts
│   ├── db_scripts/         # Database management scripts
│   └── logging.py          # Logging configuration
│
├── media/                  # User uploaded files
├── staticfiles/            # Static files
└── templates/              # Django templates
```

## Prerequisites

- **Python 3.8+**
- **Node.js 14+**
- **npm or yarn**

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/college-feedback-system.git
cd college-feedback-system
```

2. **Set up the backend**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Initialize database with sample data (optional)
python utils/db_scripts/initialize_db.py
```

3. **Set up the frontend**
```bash
cd frontend
npm install
```

4. **Start the development servers**
```bash
# Backend (in root directory)
python manage.py runserver

# Frontend (in frontend directory)
npm start
```

## Testing

The project includes a comprehensive test suite:

```bash
# Run Django tests
python manage.py test

# Run specific test module
python manage.py test tests.unit.test_feedback

# Run with coverage report
coverage run --source='.' manage.py test
coverage report

# Frontend tests
cd frontend
npm test
```

## Database Structure

The system uses the following core models:

- **User** - Custom user model with email-based authentication
- **Department** - Academic and administrative departments
- **UserProfile** - Extended user information including role and department
- **FeedbackCategory** - Categories for organizing feedback
- **Feedback** - Core feedback entries with title, content, and metadata
- **Comment** - Comments on feedback items for discussion

## API Endpoints

The system provides RESTful API endpoints for all functionality:

- **Authentication**: `/api/auth/` - Login, logout, refresh tokens
- **Users**: `/api/users/` - User management
- **Departments**: `/api/departments/` - Department listing and management
- **Feedback**: `/api/feedback/` - Feedback submission and management
- **Categories**: `/api/categories/` - Feedback category management

## Deployment

For production deployment:

1. Update `settings.py` with production settings
2. Set environment variables for sensitive information
3. Use a production-grade database (PostgreSQL recommended)
4. Set up static file serving with Nginx or CDN
5. Configure HTTPS with SSL certificate

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please create an issue in the repository or contact the administrator.