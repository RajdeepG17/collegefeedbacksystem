# College Feedback System

A comprehensive feedback management system for educational institutions built with Django and React.

## Project Structure

```
college_feedback_system/
├── accounts/           # User authentication and management
├── feedback/          # Core feedback functionality
├── frontend/          # React frontend application
├── college_feedback_system/  # Django project settings
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
└── README.md         # Project documentation
```

## Features

- User authentication and role-based access control
- Feedback submission and management
- Real-time notifications
- Admin dashboard
- Responsive web interface

## Setup Instructions

1. Clone the repository
2. Create and activate a virtual environment
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
5. Run database migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```
7. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

## Technologies Used

- Backend: Django, Django REST Framework
- Frontend: React, Material-UI
- Database: SQLite
- Authentication: Django REST Framework JWT

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details