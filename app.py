import logging
from flask import Flask, jsonify, request
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import re
from email_validator import validate_email, EmailNotValidError

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

app = Flask(__name__)

# Load Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

# Initialize Supabase client with minimal options to avoid proxy issue
try:
    supabase: Client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )
except Exception as e:
    logging.error(f"Failed to initialize Supabase client: {str(e)}")
    raise

# --- Validation Functions ---

def validate_phone_number(phone):
    pattern = r'^(\+91[\s\-]?|0)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_lead_data(data, check_existing=True):
    errors = []

    required_fields = ['name', 'phone', 'email', 'party']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field} is required")

    # Phone validation
    if 'phone' in data and data['phone']:
        if not validate_phone_number(data['phone']):
            errors.append("Invalid phone number format. Use +91 XXXXXXXXXX or 0XXXXXXXXXX")
        elif check_existing:
            try:
                result = supabase.table('leads_table').select("*").eq('phone', data['phone']).limit(1).execute()
                if result.data:
                    errors.append("Phone number already exists")
            except Exception as e:
                logging.error(f"Phone validation error: {str(e)}")
                errors.append("Error validating phone number")

    # Email validation
    if 'email' in data and data['email']:
        try:
            validate_email(data['email'])
            if check_existing:
                try:
                    result = supabase.table('leads_table').select("*").eq('email', data['email']).limit(1).execute()
                    if result.data:
                        errors.append("Email already exists")
                except Exception as e:
                    logging.error(f"Email validation error: {str(e)}")
                    errors.append("Error validating email")
        except EmailNotValidError:
            errors.append("Invalid email format")

    return errors

# --- Routes ---

@app.route('/api/leads', methods=['GET'])
def get_all_leads():
    try:
        response = supabase.table('leads_table').select("*").execute()
        return jsonify({"leads": response.data})
    except Exception as e:
        logging.error(f"Error fetching leads: {str(e)}")
        return jsonify({"message": f"Error fetching leads: {str(e)}"}), 500

@app.route('/api/leads/<int:lead_id>', methods=['GET'])
def get_lead(lead_id):
    try:
        response = supabase.table('leads_table').select("*").eq('id', lead_id).execute()
        if response.data:
            return jsonify({"lead": response.data[0]})
        return jsonify({"message": "Lead not found"}), 404
    except Exception as e:
        logging.error(f"Error fetching lead {lead_id}: {str(e)}")
        return jsonify({"message": f"Error fetching lead: {str(e)}"}), 500

@app.route('/api/leads', methods=['POST'])
def create_lead():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    errors = validate_lead_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    if 'lastconnected' not in data:
        data['lastconnected'] = datetime.now(timezone.utc).isoformat()

    data.setdefault('status', 'Connected')
    data.setdefault('tag', 'Lead')

    try:
        response = supabase.table('leads_table').insert(data).execute()
        return jsonify({"lead": response.data[0]}), 201
    except Exception as e:
        logging.error(f"Error creating lead: {str(e)}")
        return jsonify({"message": f"Error creating lead: {str(e)}"}), 500

@app.route('/api/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    try:
        existing_lead = supabase.table('leads_table').select("*").eq('id', lead_id).execute()
        if not existing_lead.data:
            return jsonify({"message": "Lead not found"}), 404

        check_existing = False
        if ('email' in data and data['email'] != existing_lead.data[0]['email']) or \
           ('phone' in data and data['phone'] != existing_lead.data[0]['phone']):
            check_existing = True

        errors = validate_lead_data(data, check_existing)
        if errors:
            return jsonify({"errors": errors}), 400

        response = supabase.table('leads_table').update(data).eq('id', lead_id).execute()
        return jsonify({"lead": response.data[0]})
    except Exception as e:
        logging.error(f"Error updating lead {lead_id}: {str(e)}")
        return jsonify({"message": f"Error updating lead: {str(e)}"}), 500

@app.route('/api/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    try:
        response = supabase.table('leads_table').delete().eq('id', lead_id).execute()
        if response.data:
            return jsonify({"message": f"Lead {lead_id} deleted successfully"})
        return jsonify({"message": "Lead not found"}), 404
    except Exception as e:
        logging.error(f"Error deleting lead {lead_id}: {str(e)}")
        return jsonify({"message": f"Error deleting lead: {str(e)}"}), 500

# --- Main ---

if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")