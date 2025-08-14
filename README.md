# Emergency QR System

A Django-based web application for generating and managing emergency QR codes. This system allows users to register, log in, and create QR codes linked to emergency information, which can be scanned for quick access in critical situations.

## Features
- User registration and authentication
- Dashboard for managing profiles and QR codes
- Emergency information form
- QR code generation and storage
- Admin interface for management

## Project Structure
```
qr_emergency_project/   # Django project settings
qr_system/              # Main app: models, views, forms, admin, management commands
media/qr_codes/         # Generated QR code images
migrations/             # Database migrations
templates/qr_system/    # HTML templates
manage.py               # Django management script
requirement.txt         # Python dependencies
```

## Setup Instructions
1. **Clone the repository**
   ```bash
   git clone https://github.com/Co-vengers/emergency_qr_system
   cd emergency_qr_system
   ```
2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirement.txt
   ```
4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Usage
- Access the app at `http://127.0.0.1:8000/`
- Register or log in to manage your profile and generate QR codes
- Admin interface available at `/admin/`

## Management Commands
- Generate initial QR codes:
  ```bash
  python manage.py generate_initial_qr_codes
  ```

## License
This project is licensed under the MIT License.
