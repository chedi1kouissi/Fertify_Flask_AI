import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_session import Session
# Try to import CORS, fallback gracefully if not available
try:
    from flask_cors import CORS
    has_cors = True
except ImportError:
    has_cors = False
import logging
from PyPDF2 import PdfReader
import base64

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Apply CORS if available
if has_cors:
    CORS(app, resources={r"/*": {"origins": "*"}})
    logger.info("CORS enabled for Disease Detection API")
else:
    logger.warning("CORS package not available, cross-origin requests may be restricted")
    
app.config.update(
    SESSION_TYPE="filesystem",
    SECRET_KEY=os.urandom(24),
    TEMPLATES_AUTO_RELOAD=True
)
Session(app)

# Set port
PORT = int(os.getenv('DISEASE_PORT', 5002))

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
    system_instruction="Act as an AI agricultural expert.just answer the question",
)


class PDFManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = self.load_content()

    def load_content(self):
        try:
            if not os.path.exists(self.file_path):
                logger.warning(f"PDF file not found: {self.file_path}")
                return self.get_default_content()
                
            with open(self.file_path, "rb") as file:
                reader = PdfReader(file)
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            logger.info("PDF content loaded successfully")
            return text
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            return self.get_default_content()

    

    def get_content(self):
        return self.content

pdf_manager = PDFManager(os.getenv('PDF_PATH', 'bismilleh.pdf'))

@app.route('/')
def index():
    # Basic health check endpoint
    return jsonify({
        "status": "ok",
        "service": "Disease Detection API",
        "version": "1.0.0"
    })

@app.route('/health')
def health_check():
    """Detailed health check endpoint"""
    try:
        # Check if the PDF content is loaded
        pdf_status = "ok" if pdf_manager.content else "error"
        pdf_content_length = len(pdf_manager.content) if pdf_manager.content else 0
        
        return jsonify({
            "status": "ok",
            "service": "Disease Detection API",
            "version": "1.0.0",
            "port": PORT,
            "pdf_data": {
                "status": pdf_status,
                "content_length": pdf_content_length,
                "path": pdf_manager.file_path,
                "exists": os.path.exists(pdf_manager.file_path)
            },
            "gemini_api": {
                "status": "configured" if GEMINI_API_KEY else "missing"
            },
            "routes": [
                {"path": "/", "methods": ["GET"], "description": "Health check"},
                {"path": "/health", "methods": ["GET"], "description": "Detailed health check"},
                {"path": "/api/predict_disease", "methods": ["POST"], "description": "API endpoint for disease prediction"},
                {"path": "/predict_disease", "methods": ["POST"], "description": "Web endpoint for disease prediction"}
            ]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# Route with and without trailing slash for better compatibility
@app.route('/predict_disease', methods=['POST'])
@app.route('/predict_disease/', methods=['POST'])
def predict_disease():
    try:
        # Check if file is in the request
        if 'image' not in request.files:
            logger.error("No image file in request")
            return jsonify({"error": "No image file provided"}), 400
            
        file = request.files['image']
        
        # Read the file and convert to base64
        image_data = base64.b64encode(file.read()).decode('utf-8')
        logger.info(f"Successfully read image file: {file.filename if hasattr(file, 'filename') else 'unknown'}")

        prompt = f"""
You are an expert AI agricultural assistant. Analyze the provided plant image and diagnose the disease by comparing its symptoms to the information in the "Extracted Disease Data" below.

### Extracted Disease Data:
{pdf_manager.get_content()}

### User Query:
Here is an image of a plant. Describe the likely disease and suggest a remedy based on the extracted data. Focus on the key identifying features observed in the image and match them to the descriptions in the "Extracted Disease Data".

### Image Analysis:
[Analyze the provided image for noticeable symptoms such as leaf spots, discoloration, growth patterns, etc. Be specific and list the observed symptoms.]

### Response Format:
If a likely match is found, provide the following:

**Likely Disease:** [Disease Name from the PDF]
**Category:** [Fungal, Bacterial, or Viral]

**Observed Symptoms Matching the Disease:**
- [Specific symptom from the image that matches a symptom in the PDF, e.g., "Leaf Symptoms: White to grayish-white powdery patches on the upper leaf surface."]
- [Another matching symptom, including the symptom category]
...

**Recommended Remedy:** [Product name from the Remedy section in the PDF]

**Application Instructions:**
- [Step-by-step instructions from the 'Application Instructions' in the PDF]
- [Include timing details]
- [Include frequency of application]
- [Include all listed safety precautions]
- [Include any other relevant instructions]

If no clear match is found based on the image and the "Extracted Disease Data", respond with:

"Based on the provided image and disease descriptions, I am unable to make a confident diagnosis. Please provide a clearer image or consult with a local agricultural expert for further assistance."
"""

        # Directly use generate_content with the multimodal content
        response = model.generate_content(
            [
                {"mime_type": "image/jpeg", "data": image_data},
                {"text": prompt}
            ]
        ).text.strip()

        logger.info("Successfully generated disease prediction")
        return jsonify({"prediction": response})
    except Exception as e:
        logger.error(f"Error in disease prediction: {e}")
        return jsonify({"error": str(e)}), 500

# API route with and without trailing slash
@app.route('/api/predict_disease', methods=['POST'])
@app.route('/api/predict_disease/', methods=['POST'])
def api_predict_disease():
    try:
        # Check if file is in the request
        if 'image' not in request.files:
            logger.error("No image file in request")
            logger.error(f"Request form data: {request.form}")
            logger.error(f"Request files: {request.files}")
            return jsonify({"error": "No image file provided"}), 400
            
        file = request.files['image']
        logger.info(f"Received file: {file.filename}")
        
        # Read the file and convert to base64
        image_data = base64.b64encode(file.read()).decode('utf-8')
        logger.info(f"Successfully read image file: {file.filename if hasattr(file, 'filename') else 'unknown'}")

        # Process the image data with the AI model
        result = process_image_with_model(image_data)
        
        logger.info("Successfully generated disease prediction")
        return jsonify({"prediction": result})
    except Exception as e:
        logger.error(f"Error in disease prediction: {e}")
        return jsonify({"error": str(e)}), 500

# New endpoint for base64-encoded images
@app.route('/api/predict_disease_base64', methods=['POST'])
def api_predict_disease_base64():
    try:
        # Get JSON data 
        json_data = request.json
        if not json_data or 'image_base64' not in json_data:
            logger.error("No base64 image data in request")
            return jsonify({"error": "No base64 image data provided"}), 400
            
        # Get base64 string from request
        image_data = json_data['image_base64']
        logger.info(f"Received base64 image data of length: {len(image_data)}")
        
        # Process the image data with the AI model
        result = process_image_with_model(image_data)
        
        logger.info("Successfully generated disease prediction from base64 image")
        return jsonify({"prediction": result})
    except Exception as e:
        logger.error(f"Error in base64 disease prediction: {e}")
        return jsonify({"error": str(e)}), 500

# Helper function to process image with AI model
def process_image_with_model(image_data):
        prompt = f"""
You are an expert AI agricultural assistant. Analyze the provided plant image and diagnose the disease by comparing its symptoms to the information in the "Extracted Disease Data" below.

### Extracted Disease Data:
{pdf_manager.get_content()}

### User Query:
Here is an image of a plant. Describe the likely disease and suggest a remedy based on the extracted data. Focus on the key identifying features observed in the image and match them to the descriptions in the "Extracted Disease Data".

### Image Analysis:
[Analyze the provided image for noticeable symptoms such as leaf spots, discoloration, growth patterns, etc. Be specific and list the observed symptoms.]

### Response Format:
If a likely match is found, provide the following:

**Likely Disease:** [Disease Name from the PDF]
**Category:** [Fungal, Bacterial, or Viral]

**Observed Symptoms Matching the Disease:**
- [Specific symptom from the image that matches a symptom in the PDF, e.g., "Leaf Symptoms: White to grayish-white powdery patches on the upper leaf surface."]
- [Another matching symptom, including the symptom category]
...

**Recommended Remedy:** [Product name from the Remedy section in the PDF]

**Application Instructions:**
- [Step-by-step instructions from the 'Application Instructions' in the PDF]
- [Include timing details]
- [Include frequency of application]
- [Include all listed safety precautions]
- [Include any other relevant instructions]

If no clear match is found based on the image and the "Extracted Disease Data", respond with:

"Based on the provided image and disease descriptions, I am unable to make a confident diagnosis. Please provide a clearer image or consult with a local agricultural expert for further assistance."
"""

        # Directly use generate_content with the multimodal content
        response = model.generate_content(
            [
                {"mime_type": "image/jpeg", "data": image_data},
                {"text": prompt}
            ]
        ).text.strip()

        return response

# Define a function to start the server
def start_server(use_reloader=True, debug=True):
    logger.info(f"Starting Disease Detection API on port {PORT}")
    logger.info(f"API endpoints available at: http://localhost:{PORT}/predict_disease/ and http://localhost:{PORT}/api/predict_disease")
    app.run(debug=debug, host='0.0.0.0', port=PORT, use_reloader=use_reloader)

if __name__ == "__main__":
    start_server()