# Political Leads Management API

A Flask-based REST API for managing political leads with Supabase integration.

## Features

- CRUD operations for leads management
- Email and phone number validation
- Duplicate check for email and phone
- Supabase integration for data storage
- Input validation and error handling

## Environment Variables

The following environment variables are required:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
FLASK_DEBUG=false  # Set to true for development
```

## Deployment Instructions

### Prerequisites

1. Create a [Render](https://render.com) account
2. Create a [Supabase](https://supabase.com) account and project

### Deployment Steps

1. Fork or clone this repository
2. Connect your repository to Render
3. Create a new Web Service
4. Configure the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Add Environment Variables:
   - Add your `SUPABASE_URL`
   - Add your `SUPABASE_KEY`
   - Set `FLASK_DEBUG=false`

### API Endpoints

- GET `/api/leads` - Get all leads
- GET `/api/leads/<id>` - Get specific lead
- POST `/api/leads` - Create new lead
- PUT `/api/leads/<id>` - Update lead
- DELETE `/api/leads/<id>` - Delete lead

## Local Development

1. Clone the repository
2. Create a `.env` file with required variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python app.py` 