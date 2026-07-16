currently hosted on https://hustlrjobs.onrender.com/

Hustlr — Django Job Board Platform

A full-stack job board web application built with Django that allows users to post jobs, apply for jobs, communicate via messaging, and manage listings in a clean, modern interface.

✨ Key Features
🔐 User authentication (signup, login, logout)
📝 Create, edit, and delete job listings
📄 Job application system with form validation
💬 Real-time-style messaging system between users
🔔 Notification system for applications and activity
🔎 Job search and category filtering
📑 Pagination for scalable job browsing
🖼 Image uploads via Cloudinary
🚨 Job reporting system for moderation
👤 User profiles with activity tracking
🛠 Tech Stack

Backend

Django 5.x
Django ORM
SQLite (development) / PostgreSQL-ready

Frontend

HTML5
CSS3
Vanilla JavaScript

Services & Tools

Cloudinary (media storage)
Whitenoise (static file handling)
python-dotenv (environment variables)
dj-database-url (database config)
🧠 Architecture Overview
Django MVT (Model–View–Template) architecture
Modular apps:
job_board → core job system
users → authentication, profiles, messaging
Environment-based configuration using .env
Media stored externally via Cloudinary
Secure settings via environment variables
📸 Screenshots
<img width="1320" height="2577" alt="image" src="https://github.com/user-attachments/assets/6d048e6e-3266-468c-94c1-4e581e758296" />
<img width="1320" height="2219" alt="image" src="https://github.com/user-attachments/assets/67721b88-6e98-4e4f-9ee6-71aa06f3a7af" />
<img width="1320" height="2292" alt="image" src="https://github.com/user-attachments/assets/7e174277-4f95-43e2-beda-85097ece1f5b" />
<img width="1320" height="2309" alt="image" src="https://github.com/user-attachments/assets/985c7849-d808-41df-ac73-07f528d0b053" />

⚙️ Installation & Setup
1. Clone repository
git clone https://github.com/gfigueroa07/job_board.git
cd job_board
2. Create virtual environment
python -m venv .venv

Activate:

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Environment setup

Create .env file:

cp .env.example .env

Then update values:

SECRET_KEY=your-secret-key
DEBUG=True

ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=sqlite:///db.sqlite3

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
5. Apply migrations
python manage.py migrate
6. Create superuser
python manage.py createsuperuser
7. Run development server
python manage.py runserver
