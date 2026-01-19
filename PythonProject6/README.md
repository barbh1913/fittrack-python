# FitTrack Gym Management System

A comprehensive full-stack gym management system built with Flask (Python) and React, implementing advanced features including queue management, smart check-in, progress tracking, and financial reporting.

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Quick Start](#quick-start)

---

## Overview

FitTrack is a production-ready gym management system that handles:

- **Member Management**: Registration, subscriptions, and profile management
- **Class Session Management**: Scheduling, enrollment, and capacity management
- **Queue Management**: Automatic waiting list with priority-based promotion (VIP members get priority)
- **Smart Check-In**: Real-time validation with 9 business rules (subscription status, debt, payment, entry limits)
- **Progress Tracking**: Workout performance logging and historical analysis
- **Financial Management**: Revenue tracking, debt management, and demand analytics
- **Role-Based Access Control**: Admin, Trainer, and Member roles with appropriate permissions

---

## Key Features

### 1. Smart Check-In System
- Validates subscription status (Active/Frozen/Expired)
- Checks remaining entries
- Validates outstanding debts
- Detects failed payments
- Enforces daily (max 3) and weekly (max 15) entry limits
- All checks logged for audit trail

### 2. Queue Management
- Automatic waiting list when sessions are full
- Priority-based queue (VIP members prioritized)
- Automatic promotion when spots become available
- Approval deadline system (24-hour window)
- High-demand detection and recommendations

### 3. Progress Tracking
- Structured workout plans with exercises, sets, reps, weights
- Long-term progress logging
- Trainer and member views
- Performance metrics and trends

### 4. Financial Management
- Revenue reports by month or plan type
- Open debts tracking
- Demand metrics (profitable/overloaded classes)
- High-demand session recommendations

---

## Architecture

The project follows a **layered architecture** with clear separation of concerns, including a dedicated Validation Layer:

```
┌─────────────────────────────────────┐
│   Interface Layer (API)              │
│   - HTTP request/response handling   │
│   - Delegates to Validation Layer    │
│   - Delegates to Business Layer      │
└──────────────┬───────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Validation Layer (Schemas/Utils)  │
│   - Input format validation         │
│   - Regex pattern validation        │
│   - Data type validation             │
│   - Required field validation        │
└──────────────┬───────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Business Logic Layer (Services)    │
│   - Business rules & validation      │
│   - Orchestrates repository calls   │
│   - Independent of HTTP/UI/DB        │
└──────────────┬───────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Data Access Layer (Repositories)   │
│   - Database CRUD operations        │
│   - Connection management           │
│   - No business logic                │
└──────────────┬───────────────────────┘
               │
               ▼
            Database
```

### Layer Responsibilities

1. **API Layer** (`backend/app/api/`)
   - Handles HTTP requests/responses
   - Collects input data
   - Delegates validation to Validation Layer
   - Delegates processing to Service layer
   - Returns formatted JSON responses

2. **Validation Layer** (`backend/app/schemas/`, `backend/app/utils/regex_patterns.py`)
   - **Input Format Validation**: Validates data types, required fields, field lengths
   - **Regex Pattern Validation**: Email, phone, ID format, full name, password patterns
   - **Data Sanitization**: Ensures data meets format requirements before business logic
   - **Error Translation**: Converts validation errors to appropriate HTTP responses
   - **Centralized Patterns**: All regex patterns stored in `utils/regex_patterns.py` for reusability

3. **Service Layer** (`backend/app/services/`)
   - Contains all business rules and validation
   - Orchestrates repository calls
   - Independent of HTTP/UI/DB details
   - Validates business constraints (uniqueness, eligibility, status checks)

4. **Repository Layer** (`backend/app/repositories/`)
   - Database CRUD operations only
   - Connection management
   - No business logic

5. **Model Layer** (`backend/app/models/`)
   - SQLAlchemy ORM models
   - Database schema definitions
   - Entity relationships

---

## Project Structure

```
PythonProject6/
├── backend/app/
│   ├── api/              # API Layer (Flask Blueprints)
│   ├── services/         # Business Logic Layer
│   ├── repositories/     # Data Access Layer
│   ├── models/           # ORM Models (SQLAlchemy)
│   ├── schemas/          # Validation Layer (Pydantic schemas)
│   ├── exceptions/       # Error Handling
│   └── utils/            # Utilities (regex patterns, etc.)
│
├── frontend/static/      # React Frontend
│   ├── src/              # React source code
│   └── dist/             # Production build
│
├── config.ini            # Database configuration
├── requirements.txt      # Python dependencies
├── seed.py              # Database seeding
└── run.py               # Application entry point
```

---

## Technologies

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **PyMySQL**: MySQL database driver
- **Python 3.x**: Programming language

### Frontend
- **React**: UI framework
- **Vite**: Build tool
- **JavaScript/JSX**: Frontend language

### Database
- **MySQL**: Relational database

---

## Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure database**: Edit `config.ini` with your MySQL credentials
3. **Initialize database**: `python seed.py`
4. **Build frontend**: `cd frontend/static && npm install && npm run build`
5. **Start server**: `python run.py`
6. **Access**: Open http://localhost:5000

For detailed setup instructions, see [HOW_TO_RUN.md](HOW_TO_RUN.md).

---

## Database Schema

### Core Entities
- **Person** (abstract): Base class for Member, Trainer, Admin
- **Member**: Gym members with subscriptions
- **Trainer**: Class instructors
- **Admin**: System administrators
- **Plan**: Subscription plans (Monthly, Yearly, Weekly, Daily, VIP)
- **Subscription**: Member subscriptions with status tracking
- **Payment**: Payment records
- **ClassSession**: Scheduled classes with capacity
- **Enrollment**: Member enrollments in sessions
- **WaitingList**: Queue entries for full sessions
- **Checkin**: Check-in records with approval/denial reasons
- **WorkoutPlan**: Personalized training plans
- **WorkoutItem**: Exercise items in plans
- **ProgressLog**: Workout performance logs

### Key Relationships
- Member → Subscriptions (1:N)
- Member → Enrollments (1:N)
- Member → Checkins (1:N)
- Subscription → Payments (1:N)
- ClassSession → Enrollments (1:N)
- ClassSession → WaitingList (1:N)
- WorkoutPlan → WorkoutItems (1:N)
- WorkoutPlan → ProgressLogs (1:N)

---

## API Endpoints

### Members
- `POST /api/members` - Create member
- `GET /api/members` - List all members
- `GET /api/members/<id>` - Get member by ID
- `PUT /api/members/<id>` - Update member

### Check-In
- `POST /api/checkin` - Process check-in

### Sessions
- `POST /api/sessions` - Create session
- `POST /api/sessions/<id>/enroll` - Enroll in session
- `POST /api/sessions/<id>/cancel` - Cancel enrollment
- `GET /api/sessions` - List all sessions

### Subscriptions
- `POST /api/subscriptions` - Assign subscription
- `POST /api/subscriptions/<id>/freeze` - Freeze subscription
- `POST /api/subscriptions/<id>/unfreeze` - Unfreeze subscription

### Financial Reports
- `GET /api/financial/revenue` - Revenue report
- `GET /api/financial/debts` - Open debts
- `GET /api/financial/demand-metrics` - Class demand metrics
- `GET /api/financial/high-demand` - High-demand sessions

For complete API documentation, see the code comments in `backend/app/api/`.

---

## OOP Principles

The project demonstrates:

1. **Encapsulation**: Private data through getters/setters, enum-based status management
2. **Inheritance**: Person base class for Member, Trainer, Admin
3. **Polymorphism**: Different subscription types handled uniformly
4. **Abstraction**: Repository pattern abstracts database operations

---

## Validation Layer

The Validation Layer ensures data integrity before processing:

### Validation Components

1. **Pydantic Schemas** (`backend/app/schemas/`)
   - Request/Response schemas for each entity
   - Field validation (types, lengths, required fields)
   - Custom validators using regex patterns
   - Automatic error message generation

2. **Regex Patterns** (`backend/app/utils/regex_patterns.py`)
   - **EMAIL_PATTERN**: Standard email format validation
   - **PHONE_PATTERN_IL**: Israeli phone format (0X-XXXXXXX)
   - **PHONE_PATTERN_INTL**: International phone format
   - **ID_PATTERN**: 9-digit member ID validation
   - **FULLNAME_PATTERN**: Name validation (2-100 chars, letters and spaces)
   - **PASSWORD_PATTERN**: Strong password requirements

### Validation Flow

```
1. API receives request
   ↓
2. Validation Layer validates input format
   - Checks required fields
   - Validates data types
   - Applies regex patterns
   ↓
3. If validation passes → Business Logic Layer
4. If validation fails → Returns 422/400 error
```


---

## Error Handling

- **Validation Errors** (422): Input format/required field errors (from Validation Layer)
- **Business Errors** (400): Business rule violations (from Service Layer)
- **Not Found** (404): Resource not found
- **Conflict** (409): Duplicate resources
- **Server Errors** (500): Internal server errors

All errors return consistent JSON responses with clear messages.

---

## Security Features

- Input validation with regex patterns
- SQL injection prevention (SQLAlchemy ORM)
- Role-based access control
- Business rule enforcement
- Audit logging (all check-ins logged)

---

## License

This project is for educational purposes.

---

For detailed setup and running instructions, see [HOW_TO_RUN.md](HOW_TO_RUN.md).
