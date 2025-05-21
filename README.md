🌾 Fertify – AI-Powered Agriculture Assistant
Fertify is a smart agriculture mobile application that leverages AI to assist farmers and growers with two core services:

Fertilizer Optimization
Get intelligent fertilizer recommendations based on soil parameters and crop type—plus actionable guidance on how to apply fertilizer efficiently for better yield and cost savings.

Plant Disease Diagnosis
Diagnose plant diseases from a simple leaf photo and receive treatment advice along with proper remedy usage instructions.

📱 Designed for field-ready mobile devices:
This system is intended to work as part of a broader smart farming ecosystem. It helps individual growers make informed decisions while providing agritech companies, agricultural cooperatives, or public institutions with scalable support tools. Future versions will integrate advanced crop scoring and growth tracking features.

🚀 Features
✅ AI-powered fertilizer recommendations tailored to soil and crop data

✅ Real-time plant disease detection using image analysis

✅ Step-by-step remedy instructions and best usage practices

✅ Built with React Native and Flask for cross-platform performance

✅ Modular backend for easy extension (e.g., pest detection, yield prediction)

📦 Prerequisites
Frontend

Node.js (v14 or higher)

npm or yarn

Expo CLI (npm install -g expo-cli)

Backend

Python 3.8+

Flask + dependencies:

bash
Copier
Modifier
pip install flask flask-cors flask-session google-generativeai PyPDF2 pandas
🧪 Getting Started
1. Start Backend Services
The backend contains two AI-powered services:

Fertilizer Service (Port 5001)

Disease Detection Service (Port 5002)

Run them as follows:

bash
Copier
Modifier
# Navigate to the backend folder
cd greenAI

# For Windows
start_services.bat

# For macOS/Linux
chmod +x start_services.sh
./start_services.sh
Check service status:

http://localhost:5001/health

http://localhost:5002/health

2. Launch the React Native App
bash
Copier
Modifier
# Navigate to the frontend folder
cd Fertify_react

# Install dependencies
npm install

# Start Expo development server
npm start
Choose how to run the app:

📱 Android device/emulator: Press a

🍏 iOS device/simulator (macOS only): Press i

🌐 Web browser: Press w

3. API Configuration (First Launch)
On app launch:

Tap the ⚙️ API Config button (top-right corner)

Enter your machine's IP address

Tap "Test Connection"

If successful, tap "Save"

💡 Ensure your mobile device and computer are on the same Wi-Fi network.

🛠 Troubleshooting
Confirm both backend services are up via /health endpoints

Double-check your local IP address is correct

Make sure devices are on the same LAN

Temporarily disable firewalls blocking ports 5001 or 5002

Restart services using start_services script

🔮 Future Enhancements
Intelligent crop scoring models

Pest detection via image and symptom inputs

Growth tracking with temporal data modeling

Offline diagnosis mode with pre-trained models

Integration with agricultural IoT sensors and platforms

📄 License
MIT Licensed. See the LICENSE file for details.

🙏 Acknowledgments
Built with React Native, Flask, and Google Generative AI

Disease diagnosis supported by machine learning and plant pathology datasets

Inspired by precision agriculture and sustainable farming principles
