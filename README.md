# Mail-Daemon 👻

Mail-Daemon is an intelligent, AI-powered email triage dashboard built with Django. It automatically fetches unread emails from your inbox, leverages Google's Gemini AI to summarize and categorize them, and stores the processed data in a serverless Neon PostgreSQL database. 

The project features a sleek web dashboard that allows users to filter emails by category, fetch new mail on demand, archive emails (syncing directly with Gmail), and instantly jump to specific threads.

## ✨ Features

* **Automated Fetching:** Securely connects to your inbox via IMAP to retrieve unread emails.
* **AI Summarization & Categorization:** Integrates with the Gemini API to read email bodies, generate concise summaries, and intelligently assign categories (e.g., Alert, Newsletter, Personal, Action Required).
* **Serverless Database:** Uses Neon Console (PostgreSQL) for fast, reliable storage of processed email metadata.
* **Interactive Dashboard:** A custom web UI featuring:
  * Real-time category filtering.
  * One-click "Fetch New Mail" trigger.
  * Direct deep-links to open the specific email in Gmail.
  * An "Archive" function that removes the email from the local dashboard *and* removes the Inbox label directly in Gmail via the Gmail API.

## 🛠️ Tech Stack

* **Backend:** Python, Django, Django REST Framework
* **AI Integration:** Google Gemini API
* **Database:** Neon DB (PostgreSQL)
* **Email Services:** `imaplib` (Fetching), Google OAuth / Gmail API (Archiving)
* **Frontend:** HTML, CSS, Vanilla JavaScript

## 📂 Project Structure

```text
mail-daemon/
├── core/                   # Main Django project settings and routing
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dropbox/                # Primary application handling emails and UI
│   ├── models.py           # Database schema (EmailMessage)
│   ├── views.py            # Web dashboard and API endpoints
│   ├── services/           # Core logic modules
│   │   ├── ai_parser.py    # Gemini API integration
│   │   ├── fetcher.py      # IMAP email retrieval
│   │   └── gmail_api.py    # Google OAuth & Gmail archiving logic
│   ├── templates/
│   │   └── dashboard.html  # Main UI template
│   └── static/             # CSS, JS, and Images (Ghost favicon)
├── build.sh                # Deployment build script (e.g., for Render)
└── requirements.txt        # Python dependencies
```

## 🚀 Local Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/mail-daemon.git
cd mail-daemon
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory (next to `manage.py`) and add the following credentials:

```ini
# Django Setup
SECRET_KEY=your_django_secret_key
DEBUG=True

# Neon Database
DATABASE_URL=postgres://user:password@ep-cool-name.region.aws.neon.tech/dbname

# Email Fetcher (IMAP)
EMAIL_USER=your_email@gmail.com
EMAIL_APP_PASSWORD=your_16_digit_app_password
EMAIL_HOST=imap.gmail.com

# AI Parser
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Google API Credentials (For Archiving)
To enable the 2-way sync archiving feature, you must place a `credentials.json` file (generated from the Google Cloud Console for a Desktop App) in the root directory. Upon first run, the app will prompt you to log in and generate a `token.json` file.

### 6. Run Migrations
Apply the database schema to your Neon DB:
```bash
python manage.py migrate
```

### 7. Start the Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser to view the dashboard!

## 🚢 Deployment

This project includes a `build.sh` script configured for easy deployment on platforms like Render. It automatically handles dependency installation, static file collection, and database migrations during the build phase.

## 📄 License
This project is licensed under the MIT License.
