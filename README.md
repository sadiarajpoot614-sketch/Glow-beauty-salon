# Glow Beauty Salon

A modern **Beauty Salon Appointment Booking System** built with **FastAPI**.

## Features

* Online appointment booking
* Email OTP verification
* Appointment date and time selection
* Available time slots
* Duplicate booking prevention
* Customer booking confirmation email
* Salon notification email
* Admin CRM dashboard
* Appointment management

## Technologies Used

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* HTML
* CSS
* Jinja2 Templates
* FastAPI-Mail
* Python Dotenv

## Project Structure

```text
Beauty Salon/
│
├── app/
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   │
│   ├── templates/
│   │   ├── home.html
│   │   ├── about.html
│   │   ├── services.html
│   │   ├── contact.html
│   │   └── crm.html
│   │
│   ├── database.py
│   ├── main.py
│   └── models.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/sadiarajpoot614-sketch/Glow-beauty-salon.git
```

Go to the project folder:

```bash
cd Glow-beauty-salon
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file and add your database and email credentials:

```env
DATABASE_URL=your_database_url

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
```

⚠️ **Never upload your `.env` file to GitHub.**

## Run the Project

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open your browser:

```text
http://127.0.0.1:8000
```
## License

This project is created for educational purposes.
