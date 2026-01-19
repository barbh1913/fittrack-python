# 🚀 How to Run the Project

Step-by-step guide to set up and run the FitTrack Gym Management System.

---

## Prerequisites

- **Python 3.8+** installed
- **MySQL** server installed and running
- **Node.js** and **npm** installed (for frontend)
- **Git** (optional, for cloning)

---

## Step 1: Install Python Dependencies

**Option A: Use batch file (Windows)**
```bash
install-requirements.bat
```

**Option B: Manual (Windows)**
```bash
py -m pip install -r requirements.txt
```

**Option C: Manual (Linux/Mac)**
```bash
pip3 install -r requirements.txt
# or
python3 -m pip install -r requirements.txt
```

**Required packages:**
- Flask (web framework)
- flask-cors (CORS support for React frontend)
- SQLAlchemy (ORM for database)
- PyMySQL (MySQL database driver)
- Pydantic (data validation)
- configparser (configuration file parsing)
- requests (HTTP client for testing)

---

## Step 2: Configure Database

1. Open `config.ini` in a text editor
2. Update database connection details:

```ini
[mysql]
host = localhost
port = 3306
database = gym_db
user = root
password = YOUR_MYSQL_PASSWORD
```

**Important:** Replace `YOUR_MYSQL_PASSWORD` with your actual MySQL root password.

---

## Step 3: Initialize Database

**Option A: Use batch file (Windows)**
```bash
run-seed.bat
```

**Option B: Manual (Windows)**
```bash
py seed.py
```

**Option C: Manual (Linux/Mac)**
```bash
python3 seed.py
```

**What this does:**
- Tests database connection
- Creates database if it doesn't exist
- Creates all tables (members, subscriptions, sessions, etc.)
- Inserts sample data (members, trainers, admins, plans, subscriptions)

**Expected output:**
```
✅ Connection successful!
✅ Database 'gym_db' created or already exists
✅ Tables created successfully
✅ Sample data inserted
```

---

## Step 4: Install Frontend Dependencies

Navigate to frontend directory and install npm packages:

**Option A: Use batch file (Windows)**
```bash
start-react.bat
```
(This will also build the React app - see Step 5)

**Option B: Manual**
```bash
cd frontend\static
npm install
cd ..\..
```

**Required packages:**
- React (UI framework)
- React DOM (React rendering)
- React Router DOM (client-side routing)
- Vite (build tool and dev server)
- @vitejs/plugin-react (Vite React plugin)

**Note:** This may take a few minutes on first run.

---

## Step 5: Build Frontend (Production)

**Option A: Use batch file (Windows)**
```bash
start-react.bat
```

**Option B: Manual (Windows)**
```bash
cd frontend\static
npm run build
cd ..\..
```

**Option C: Manual (Linux/Mac)**
```bash
cd frontend/static
npm run build
cd ../..
```

**What this does:**
- Builds React app for production
- Outputs to `frontend/static/dist/`
- Optimizes and bundles all assets

---

## Step 6: Start the Server

**Option A: Use batch file (Windows)**
```bash
start-flask.bat
```

**Option B: Manual (Windows)**
```bash
py run.py
```

**Option C: Manual (Linux/Mac)**
```bash
python3 run.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
```

---

## Step 7: Access the Application

1. Open your web browser
2. Navigate to: **http://localhost:5000**
3. The application should load

---

## Default Login Credentials

After running `seed.py`, you can login with these test accounts:

### Admin
- **Role:** Admin
- **ID:** `ADMIN001` or `ADMIN002`

### Trainer
- **Role:** Trainer
- **ID:** `TR001`, `TR002`, or `TR003`

### Member
- **Role:** Member
- **ID:** `123456789`, `987654321`, `111222333`, `444555666`, or `777888999`

---

## Development Mode (Optional)

For development with hot-reload:

### Terminal 1: Start Flask Backend

**Windows:**
```bash
py run.py
```

**Linux/Mac:**
```bash
python3 run.py
```

### Terminal 2: Start React Dev Server

**Windows:**
```bash
start-dev.bat
```

**Linux/Mac (Manual):**
```bash
cd frontend/static
npm run dev
```

**Note:** 
- React dev server runs on **http://localhost:5173**
- Flask API runs on **http://localhost:5000**
- React proxies API calls to Flask automatically

---

## Troubleshooting

### Python/Pip Issues

**Problem:** `pip is not recognized` or `python is not recognized`
- **Solution (Windows):** Use `py -m pip` instead of `pip`, or `py` instead of `python`
- **Solution (Linux/Mac):** Use `python3 -m pip` and `python3` instead

**Problem:** `ModuleNotFoundError` when running scripts
- **Solution:** Make sure you installed all requirements: `py -m pip install -r requirements.txt`

### Database Connection Issues
