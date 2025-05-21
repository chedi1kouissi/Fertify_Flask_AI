import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
# Try to import CORS, fallback gracefully if not available
try:
    from flask_cors import CORS
    has_cors = True
except ImportError:
    has_cors = False
import pandas as pd
from datetime import datetime
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#fertilizer_recommendation = {'Urea':'C:\Users\ASUS\OneDrive\Bureau\fertilizer_predictor\fertilzer_images\UREA.jpg',
 #                            'Dap':'C:\Users\ASUS\OneDrive\Bureau\fertilizer_predictor\fertilzer_images\DAP.jpg'
                             
  #                           }

app = Flask(__name__)
# Update the CORS configuration to ensure headers are properly set
if has_cors:
    CORS(app, resources={r"/*": {"origins": "*"}})
    logger.info("CORS enabled for Fertilizer API")
else:
    logger.warning("CORS package not available, cross-origin requests may be restricted")
    
app.config.update(
    SESSION_TYPE="filesystem",
    SECRET_KEY=os.urandom(24),
    TEMPLATES_AUTO_RELOAD=True
)
Session(app)

# Set port
PORT = int(os.getenv('FERTILIZER_PORT', 5001))

# Set API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDn0e3pd8ZAOhYl6rS0EUf7_YKxZl0mgYU')
genai.configure(api_key=GEMINI_API_KEY)


generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 65536,
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    system_instruction="Act as an AI agricultural expert."

)


class DatasetManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.load_data()

    def load_data(self):
        try:
            if not os.path.exists(self.file_path):
                logger.warning(f"Dataset file not found: {self.file_path}")
                logger.info("Creating default dataset for fertilizer recommendations")
                self.create_default_dataset()
            else:
                self.data = pd.read_csv(self.file_path)
                logger.info("Dataset loaded successfully from file")
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            logger.info("Falling back to default dataset")
            self.create_default_dataset()

    def create_default_dataset(self):
        # Create a default dataset for basic recommendations
        logger.info("Default dataset created successfully")

        # Save the default dataset for future use
        try:
            self.data.to_csv(self.file_path, index=False)
            logger.info(f"Default dataset saved to {self.file_path}")
        except Exception as e:
            logger.warning(f"Could not save default dataset to file: {e}")

    def get_content(self):
        return self.data.to_string(index=False) if self.data is not None else ""


dataset_manager = DatasetManager(os.getenv('DATASET_PATH', 'dataset.csv'))


@app.route('/')
def index():
    # Basic health check endpoint
    return jsonify({
        "status": "ok",
        "service": "Fertilizer Recommendation API",
        "version": "1.0.0"
    })

@app.route('/health')
def health_check():
    """Detailed health check endpoint"""
    try:
        # Check if the dataset is loaded
        dataset_status = "ok" if dataset_manager.data is not None else "error"
        
        return jsonify({
            "status": "ok",
            "service": "Fertilizer Recommendation API",
            "version": "1.0.0",
            "port": PORT,
            "dataset": {
                "status": dataset_status,
                "rows": len(dataset_manager.data) if dataset_manager.data is not None else 0,
                "path": dataset_manager.file_path
            },
            "gemini_api": {
                "status": "configured" if GEMINI_API_KEY else "missing"
            },
            "routes": [
                {"path": "/", "methods": ["GET"], "description": "Health check"},
                {"path": "/health", "methods": ["GET"], "description": "Detailed health check"},
                {"path": "/api/predict_fertilizer", "methods": ["POST"], "description": "API endpoint for fertilizer prediction"},
                {"path": "/predict_fertilizer", "methods": ["POST"], "description": "Web endpoint for fertilizer prediction"}
            ]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# Route with and without trailing slash for better compatibility
@app.route('/predict_fertilizer', methods=['POST'])
@app.route('/predict_fertilizer/', methods=['POST'])
def predict_fertilizer():
    try:
        data = request.json
        
        user_message = {
            "pH": data.get("pH"),
            "Nitrogen": data.get("Nitrogen"),
            "Phosphorus": data.get("Phosphorus"),
            "Potassium": data.get("Potassium"),
            "Temperature": data.get("temperature"),
            "Humidity": data.get("humidity"),
            "Moisture": data.get("moisture"),
            "Soil Type": data.get("territory_type"),
            "Crop Type": data.get("crop_type"),
        }

        prompt = f"""
        You are an AI agricultural expert working for our company. Your task is to analyze the given soil and crop conditions and recommend the best fertilizer. Additionally, you should provide step-by-step instructions on how to use the fertilizer efficiently.

### **Fertilizer Prediction:**
Based on the provided dataset and user input, determine the most suitable fertilizer.

#### **Dataset Context:**
{dataset_manager.get_content()}

#### **User Input (Soil & Crop Conditions):**
{user_message}

- **Predict the most suitable fertilizer. Use the dataset context to recommend the best fertilizer  without any explanation or justification.** Return only the fertilizer name.

---

### **Fertilizer Application Guide:**
Once you have identified the best fertilizer, provide a clear and structured guide on how to apply it efficiently based on:
- The soil type
- The crop type
- Weather conditions (temperature, humidity, moisture)
- Best time to apply the fertilizer
- Precautions and best practices to avoid over-fertilization

**Important:** 
- Keep the response **concise and structured**.
- If the input data does not match any fertilizer recommendation with high confidence, respond with:  
  "I'm unable to determine the best fertilizer. Please consult one of our agriculture experts for personalized guidance."
        """

        chat = model.start_chat(history=[])
        response = chat.send_message(prompt).text.strip()

        if 'chat_history' not in session:
            session['chat_history'] = []
        session['chat_history'].append((str(user_message), response))
        session.modified = True

        return jsonify({"fertilizer": response})

    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        return jsonify({"error": str(e)}), 500

# API route with and without trailing slash
@app.route('/api/predict_fertilizer', methods=['POST'])
@app.route('/api/predict_fertilizer/', methods=['POST'])
def api_predict_fertilizer():
    try:
        data = request.json
        
        user_message = {
            "pH": data.get("pH"),
            "Nitrogen": data.get("Nitrogen"),
            "Phosphorus": data.get("Phosphorus"),
            "Potassium": data.get("Potassium"),
            "Temperature": data.get("temperature"),
            "Humidity": data.get("humidity"),
            "Moisture": data.get("moisture"),
            "Soil Type": data.get("territory_type"),
            "Crop Type": data.get("crop_type"),
        }

        prompt = f"""
        You are an AI agricultural expert working for our company. Your task is to analyze the given soil and crop conditions and recommend the best fertilizer. Additionally, you should provide step-by-step instructions on how to use the fertilizer efficiently.

### **Fertilizer Prediction:**
Based on the provided dataset and user input, determine the most suitable fertilizer.

#### **Dataset Context:**
{dataset_manager.get_content()}

#### **User Input (Soil & Crop Conditions):**
{user_message}

- **Predict the most suitable fertilizer. Use the dataset context to recommend the best fertilizer  without any explanation or justification.** Return only the fertilizer name.

---

### **Fertilizer Application Guide:**
Once you have identified the best fertilizer, provide a clear and structured guide on how to apply it efficiently based on:
- The soil type
- The crop type
- Weather conditions (temperature, humidity, moisture)
- Best time to apply the fertilizer
- Precautions and best practices to avoid over-fertilization

**Important:** 
- Keep the response **concise and structured**.
- If the input data does not match any fertilizer recommendation with high confidence, respond with:  
  "I'm unable to determine the best fertilizer. Please consult one of our agriculture experts for personalized guidance."
        """

        chat = model.start_chat(history=[])
        response = chat.send_message(prompt).text.strip()

        return jsonify({"fertilizer": response})

    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    session['chat_history'] = []
    return jsonify({"status": "success"})

# Define a function to start the server
def start_server(use_reloader=True, debug=True):
    logger.info(f"Starting Fertilizer Recommendation API on port {PORT}")
    logger.info(f"API endpoints available at: http://localhost:{PORT}/predict_fertilizer/ and http://localhost:{PORT}/api/predict_fertilizer")
    app.run(debug=debug, host='0.0.0.0', port=PORT, use_reloader=use_reloader)

if __name__ == "__main__":
    start_server()