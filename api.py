from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager, create_access_token
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import pandas as pd
from flask_cors import CORS
import matplotlib.pyplot as plt
from transformers import pipeline as hf_pipeline
from datetime import datetime, timedelta
import requests
from pyngrok import ngrok

public_url = ngrok.connect(5000)
print("Ngrok URL:", public_url)

# Automatically get ngrok URL from Colab
def get_colab_ngrok_url():
    try:
        response = requests.get("http://localhost:4040/api/tunnels")  # ngrok's API
        tunnels = response.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "http":
                return tunnel["public_url"]
    except Exception as e:
        print("Error fetching ngrok URL:", e)
    return None

# Flask app and configurations
app = Flask(__name__)
app.config["SECRET_KEY"] = "SECURITY"
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)  # Enable CORS for all routes

# MongoDB connection
MONGO_URI = "mongodb+srv://sm12409:6eVs23fTJdauKfea@clientscluster.slmpn.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["clients"]
users_collection = db["users"]
transactions_collection = db["transactions"]

COLAB_AI_URL = get_colab_ngrok_url()

# Ensure unique email for users
users_collection.create_index("email", unique=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"error": "User already exists"}), 400
    
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    users_collection.insert_one({
        "name": data["name"],
        "email": data["email"],
        "password": hashed_password
    })
    
    new_user = users_collection.find_one({"email": data["email"]})
    if new_user:
        print("User successfully registered:", new_user)
    else:
        print("Registration failed!")

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = users_collection.find_one({"email": data["email"]})
    if user and bcrypt.check_password_hash(user["password"], data["password"]):
        access_token = create_access_token(identity=user["email"])
        return jsonify({"access_token": access_token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/upload_csv', methods=['POST'])
@jwt_required()
def upload_csv():
    current_user_email = get_jwt_identity()
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        df = pd.read_csv(file)
        transactions = df.to_dict(orient="records")
        for transaction in transactions:
            transaction["email"] = current_user_email
        transactions_collection.insert_many(transactions)
        return jsonify({"message": "Transactions uploaded successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_email = get_jwt_identity()
    transactions = list(transactions_collection.find({"email": current_user_email}, {"_id": 0}))
    return jsonify(transactions), 200

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    users_collection.delete_one({"email": email})
    transactions_collection.delete_many({"email": email})  # Optional: delete related transactions

    return jsonify({'message': f'User {email} deleted successfully'}), 200

@app.route('/process_transactions', methods=['POST'])
@jwt_required()
def process_transactions_api():
    current_user_email = get_jwt_identity()
    data = request.json['data']
    state_tier = request.json['state_tier']
    total_savings = request.json['total_savings']
    goals = request.json['goals']

    # Forward data to Colab AI with the JWT token
    token = request.headers.get('Authorization')  # Reuse the existing token
    headers = {"Authorization": token}

    try:
        response = requests.post(f"{COLAB_AI_URL}/process_transactions", json={
            "data": data,
            "state_tier": state_tier,
            "total_savings": total_savings,
            "goals": goals
        }, headers=headers)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "AI processing failed"}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/apply_additional_funding', methods=['POST'])
@jwt_required()
def apply_additional_funding_api():
    current_user_email = get_jwt_identity()
    goals = request.json['goals']
    monthly_savings = request.json['monthly_savings']

    # Forward data to Colab AI with the JWT token
    token = request.headers.get('Authorization')  # Reuse the existing token
    headers = {"Authorization": token}

    try:
        response = requests.post(f"{COLAB_AI_URL}/apply_additional_funding", json={
            "goals": goals,
            "monthly_savings": monthly_savings
        }, headers=headers)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "AI processing failed"}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)