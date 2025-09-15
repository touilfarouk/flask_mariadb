# Personnel Management System - Deployment Guide

## Quick Start

### Prerequisites
- Python 3.8 or higher
- MariaDB or MySQL database
- Modern web browser

### Installation Steps

1. **Clone/Download the project**
   ```bash
   cd c:\Users\ASUS\Documents\protected
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Database**
   ```bash
   python setup_database.py
   ```

4. **Start the API Server**
   ```bash
   python api/main.py
   ```
   Server will run on: `http://127.0.0.1:3000`

5. **Access the Frontend**
   - Open `frontend/login.html` in a web browser
   - Or use Live Server extension in VS Code

### Default Login Credentials
- **Admin**: admin@example.com / admin123
- **Role**: Administrator with full access

## System Architecture

### Backend (Flask API)
- **Framework**: Flask with CORS support
- **Database**: MariaDB with PyMySQL connector
- **Authentication**: JWT tokens with bcrypt password hashing
- **Port**: 3000

### Frontend
- **Framework**: Vanilla JavaScript with Alpine.js
- **Styling**: TailwindCSS
- **Icons**: Font Awesome
- **Features**: Dark/Light theme toggle, responsive design

### Database Schema
```sql
Tables:
- users (id, firstname, lastname, email, password, role)
- personnel (id, matricule, nom, qualification, affectation)
- section (id, code_section, label, unit, type)
- personnel_section (personnel_id, section_id)
- user_roles (user_id, role_id)
- user_section (user_id, section_id)
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `GET /protected` - Test protected route

### Personnel Management
- `GET /personnel/all` - List all personnel
- `GET /personnel/{id}` - Get specific personnel
- `GET /personnel/{id}/sections` - Get personnel sections
- `POST /personnel/add` - Create new personnel
- `PUT /personnel/{id}` - Update personnel
- `DELETE /personnel/{id}` - Delete personnel

### Section Management
- `GET /section/all` - List all sections
- `POST /section/add` - Create new section
- `PUT /section/{id}` - Update section
- `DELETE /section/{id}` - Delete section

## Configuration

### Database Configuration (`api/config.py`)
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'comptabilite',
    'charset': 'utf8mb4'
}

SECRET_KEY = 'your-secret-key-here'
```

### Security Features
- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- CORS configuration for cross-origin requests
- Input validation and sanitization

## Features Overview

### Personnel Management
- Create, read, update, delete personnel records
- Multi-section assignment support
- Unique matricule validation
- Required field validation

### Section Management
- Full CRUD operations for organizational sections
- Section assignment to personnel
- Validation for section relationships

### User Interface
- Professional, modern design
- Dark/light theme toggle
- Responsive layout for all devices
- Intuitive navigation
- Real-time form validation
- Success/error notifications

### Authentication System
- Secure user registration
- JWT-based login system
- Role-based access (admin/customer)
- Protected routes
- Automatic token management

## Testing

### Run Comprehensive Tests
```bash
python comprehensive_test.py
```

### Run Personnel Update Tests
```bash
python test_personnel_update.py
```

### Run Frontend Integration Tests
```bash
python test_frontend_integration.py
```

## Production Deployment

### Environment Variables
Create a `.env` file for production:
```
SECRET_KEY=your-production-secret-key
DB_HOST=your-db-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=comptabilite
```

### Security Recommendations
1. Use HTTPS in production
2. Set strong SECRET_KEY
3. Configure proper database credentials
4. Enable database SSL if available
5. Implement rate limiting
6. Set up proper logging

### Performance Optimization
1. Use production WSGI server (Gunicorn, uWSGI)
2. Configure database connection pooling
3. Enable gzip compression
4. Implement caching strategies
5. Optimize database queries

## Troubleshooting

### Common Issues

**Database Connection Error**
- Check MariaDB/MySQL is running
- Verify database credentials in config.py
- Ensure database 'comptabilite' exists

**Token Authentication Issues**
- Check SECRET_KEY configuration
- Verify token expiration settings
- Clear browser localStorage if needed

**CORS Issues**
- Ensure Flask-CORS is properly configured
- Check frontend URL matches CORS settings

**Frontend Not Loading**
- Verify API server is running on port 3000
- Check browser console for JavaScript errors
- Ensure all static files are accessible

### Debug Mode
Enable debug mode for development:
```python
app.run(debug=True, host='0.0.0.0', port=3000)
```

## File Structure
```
protected/
├── api/
│   ├── auth/
│   │   └── auth.py
│   ├── personnel/
│   │   └── personnel.py
│   ├── section/
│   │   └── section.py
│   ├── utils/
│   │   └── auth.py
│   ├── config.py
│   ├── main.py
│   └── sql.sql
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js
│   │   ├── login.js
│   │   ├── main.js
│   │   ├── personnel.js
│   │   ├── protected.js
│   │   ├── register.js
│   │   └── section.js
│   ├── index.html
│   ├── login.html
│   ├── personnel.html
│   ├── register.html
│   └── section.html
├── requirements.txt
├── setup_database.py
└── README.md
```

## Support

### Documentation
- API endpoints documented in code
- Frontend components well-commented
- Database schema in sql.sql

### Testing Coverage
- Unit tests for all API endpoints
- Integration tests for frontend
- Edge case validation
- Security testing

### Maintenance
- Regular database backups recommended
- Monitor log files for errors
- Update dependencies periodically
- Review security settings regularly

---

**System Status**: Production Ready ✅
**Last Updated**: January 15, 2025
**Version**: 1.0
