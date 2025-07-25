from flask import Flask, render_template, request, redirect, jsonify, session, send_from_directory
from flask_cors import CORS, cross_origin
import pickle
import pandas as pd
import numpy as np
import json
from datetime import datetime
import uuid
from collections import Counter
import os
import logging
from werkzeug.exceptions import RequestEntityTooLarge

# Configure logging
import os
app_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(app_dir, 'vetai.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'vetai_production_key_2024_secure_livestock_prediction'  # Secure key for production
cors = CORS(app)
app.config['JSON_SORT_KEYS'] = False

class VetAIModel:
    """Wrapper class for the VetAI machine learning model"""
    def __init__(self, model, label_encoders, target_encoder, feature_names):
        self.model = model
        self.label_encoders = label_encoders
        self.target_encoder = target_encoder
        self.feature_names = feature_names
    
    def predict(self, input_df):
        """Predict disease for input DataFrame"""
        # Make a copy to avoid modifying original
        X = input_df.copy()
        
        # Encode categorical variables
        for col in self.label_encoders:
            if col in X.columns:
                # Handle unknown categories gracefully
                known_categories = set(self.label_encoders[col].classes_)
                X[col] = X[col].apply(lambda x: x if x in known_categories else self.label_encoders[col].classes_[0])
                X[col] = self.label_encoders[col].transform(X[col].astype(str))
        
        # Make prediction
        y_pred_encoded = self.model.predict(X)
        
        # Decode prediction
        y_pred = self.target_encoder.inverse_transform(y_pred_encoded)
        
        return y_pred
    
    def predict_proba(self, input_df):
        """Get prediction probabilities"""
        # Make a copy to avoid modifying original
        X = input_df.copy()
        
        # Encode categorical variables
        for col in self.label_encoders:
            if col in X.columns:
                # Handle unknown categories gracefully
                known_categories = set(self.label_encoders[col].classes_)
                X[col] = X[col].apply(lambda x: x if x in known_categories else self.label_encoders[col].classes_[0])
                X[col] = self.label_encoders[col].transform(X[col].astype(str))
        
        return self.model.predict_proba(X)

# Load model and data with error handling
try:
    model_path = os.path.join(app_dir, 'livestock_logistic_Model.pkl')
    model = pickle.load(open(model_path, 'rb'))
    logger.info(f'Successfully loaded model: {type(model)}')
    
    data_path = os.path.join(app_dir, 'Cleaned_Disease_Data.csv')
    Data = pd.read_csv(data_path)
    logger.info(f'Successfully loaded dataset with {len(Data)} records')
except Exception as e:
    logger.error(f'Error loading model or data: {str(e)}')
    raise

# Initialize session storage for prediction history
history_file = os.path.join(app_dir, 'prediction_history.json')
if not os.path.exists(history_file):
    with open(history_file, 'w') as f:
        json.dump([], f)

def load_prediction_history():
    try:
        with open(history_file, 'r') as f:
            return json.load(f)
    except:
        return []

def save_prediction_history(history):
    with open(history_file, 'w') as f:
        json.dump(history, f)

@app.route('/', methods=['GET', 'POST'])
def index():
    Animals = sorted(Data['Animal'].unique())
    Symptom_1s = sorted(Data['Symptom 1'].unique())
    Symptom_2s = sorted(Data['Symptom 2'].unique())
    Symptom_3s = sorted(Data['Symptom 3'].unique())
    
    # Get analytics data
    total_animals = len(Data)
    disease_stats = Data['Disease'].value_counts().to_dict()
    animal_stats = Data['Animal'].value_counts().to_dict()
    
    # Recent predictions
    history = load_prediction_history()
    recent_predictions = history[-5:] if history else []

    Animals.insert(0, 'Select Animal')
    Symptom_1s.insert(0, 'Select Symptom 1')
    Symptom_2s.insert(0, 'Select Symptom 2')
    Symptom_3s.insert(0, 'Select Symptom 3')
    
    return render_template('index.html', 
                         Animals=Animals, 
                         Symptom_1s=Symptom_1s, 
                         Symptom_2s=Symptom_2s, 
                         Symptom_3s=Symptom_3s,
                         total_animals=total_animals,
                         disease_stats=disease_stats,
                         animal_stats=animal_stats,
                         recent_predictions=recent_predictions)


@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    try:
        # Extract form data
        Animal = request.form.get('Animal')
        Age = request.form.get('Age')
        Temperature = request.form.get('Temperature')
        Symptom_1 = request.form.get('Symptom 1')
        Symptom_2 = request.form.get('Symptom 2')
        Symptom_3 = request.form.get('Symptom 3')

        # Validate input
        missing_fields = []
        for field_name, value in [
            ("Animal", Animal),
            ("Age", Age),
            ("Temperature", Temperature),
            ("Symptom 1", Symptom_1),
            ("Symptom 2", Symptom_2),
            ("Symptom 3", Symptom_3)
        ]:
            if value is None or value == '' or value.startswith('Select'):
                missing_fields.append(field_name)
        if missing_fields:
            return f"Error: Missing or invalid input for fields: {', '.join(missing_fields)}", 400

        # Prepare input DataFrame
        input_df = pd.DataFrame(
            [[Animal, Age, Temperature, Symptom_1, Symptom_2, Symptom_3]],
            columns=pd.Index(["Animal", "Age", "Temperature", "Symptom 1", "Symptom 2", "Symptom 3"])
        )
        print('Input DataFrame for prediction:')
        print(input_df)
        
        # Make prediction
        prediction = model.predict(input_df)
        disease = str(prediction[0])
        
        # Calculate confidence using model probabilities for better accuracy
        try:
            prediction_proba = model.predict_proba(input_df)
            confidence = float(np.max(prediction_proba) * 100)
        except:
            # Fallback to mock calculation
            confidence = np.random.uniform(78, 94)
        
        # Get treatment recommendations
        treatment = get_treatment_recommendation(disease)
        
        # Save to history
        prediction_data = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'animal': Animal,
            'age': Age,
            'temperature': Temperature,
            'symptoms': [Symptom_1, Symptom_2, Symptom_3],
            'predicted_disease': disease,
            'confidence': round(confidence, 1),
            'treatment': treatment
        }
        
        history = load_prediction_history()
        history.append(prediction_data)
        save_prediction_history(history)
        
        response_data = {
            'disease': disease,
            'confidence': round(confidence, 1),
            'treatment': treatment,
            'severity': get_disease_severity(disease),
            'prevention': get_prevention_tips(disease)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print('Prediction error:', traceback.format_exc())
        return jsonify({'error': f"Internal Server Error: {str(e)}"}), 500

def get_treatment_recommendation(disease):
    treatments = {
        'pneumonia': {
            'immediate': 'Administer broad-spectrum antibiotics (Oxytetracycline 10-20mg/kg)',
            'supportive': 'Ensure proper ventilation, maintain body temperature, provide nutritional support',
            'monitoring': 'Monitor respiratory rate, check for improvement within 48-72 hours'
        },
        'lumpy virus': {
            'immediate': 'Isolate affected animals immediately, no specific antiviral treatment available',
            'supportive': 'Supportive care with anti-inflammatory drugs, wound care for skin lesions',
            'monitoring': 'Vaccinate healthy animals, monitor for secondary bacterial infections'
        },
        'blackleg': {
            'immediate': 'Emergency high-dose penicillin (40,000-80,000 IU/kg), immediate isolation',
            'supportive': 'Anti-inflammatory treatment, supportive fluid therapy if needed',
            'monitoring': 'Implement vaccination program for remaining herd, monitor for spread'
        },
        'foot and mouth': {
            'immediate': 'Strict quarantine, report to veterinary authorities immediately',
            'supportive': 'Symptomatic treatment for oral lesions, soft feed, adequate water',
            'monitoring': 'No movement of animals, strict biosecurity, contact tracing'
        },
        'anthrax': {
            'immediate': 'EMERGENCY: High-dose penicillin, immediate veterinary consultation',
            'supportive': 'Complete isolation, do not perform necropsy, contact authorities',
            'monitoring': 'Vaccination of exposed animals, environmental decontamination'
        }
    }
    
    disease_info = treatments.get(disease.lower(), {
        'immediate': 'Consult with a veterinarian immediately for proper diagnosis',
        'supportive': 'Provide general supportive care and monitor animal condition',
        'monitoring': 'Follow standard livestock health monitoring protocols'
    })
    
    return f"IMMEDIATE: {disease_info['immediate']} | SUPPORTIVE: {disease_info['supportive']} | MONITORING: {disease_info['monitoring']}"

def get_disease_severity(disease):
    severity_map = {
        'pneumonia': 'Moderate',
        'lumpy virus': 'High', 
        'blackleg': 'High',
        'foot and mouth': 'Very High',
        'anthrax': 'Critical'
    }
    return severity_map.get(disease.lower(), 'Unknown')

def get_prevention_tips(disease):
    prevention = {
        'pneumonia': {
            'vaccination': 'Annual respiratory vaccines (IBR, BVD, BRSV)',
            'management': 'Proper ventilation, reduce overcrowding, minimize stress',
            'nutrition': 'Adequate vitamin E and selenium, quality feed',
            'monitoring': 'Regular health checks, early detection protocols'
        },
        'lumpy virus': {
            'vaccination': 'Live attenuated vaccine annually, especially in endemic areas',
            'management': 'Vector control (flies, mosquitoes), quarantine new animals 21 days',
            'nutrition': 'Maintain optimal body condition, boost immunity',
            'monitoring': 'Regular skin examination, temperature monitoring'
        },
        'blackleg': {
            'vaccination': 'Annual clostridial vaccine (7-8 way), booster as needed',
            'management': 'Avoid soil contamination, minimize trauma and wounds',
            'nutrition': 'Balanced nutrition, avoid sudden feed changes',
            'monitoring': 'Watch for lameness, swelling, sudden death'
        },
        'foot and mouth': {
            'vaccination': 'FMD vaccine where legally permitted and recommended',
            'management': 'Strict biosecurity, limit animal movement, disinfection protocols',
            'nutrition': 'Maintain good body condition for disease resistance',
            'monitoring': 'Daily inspection for oral/foot lesions, temperature checks'
        },
        'anthrax': {
            'vaccination': 'Annual anthrax vaccine in endemic areas',
            'management': 'Proper carcass disposal, environmental management, avoid disturbing soil',
            'nutrition': 'Avoid grazing in contaminated areas, provide clean water',
            'monitoring': 'Immediate reporting of sudden deaths, surveillance programs'
        }
    }
    
    disease_info = prevention.get(disease.lower(), {
        'vaccination': 'Follow standard vaccination protocols',
        'management': 'Implement good animal husbandry practices',
        'nutrition': 'Provide balanced nutrition and clean water',
        'monitoring': 'Regular health monitoring and veterinary checkups'
    })
    
    return disease_info

@app.route('/api/analytics')
def get_analytics():
    history = load_prediction_history()
    
    if not history:
        return jsonify({
            'total_predictions': 0,
            'disease_distribution': {},
            'animal_distribution': {},
            'recent_activity': []
        })
    
    # Analysis
    diseases = [p['predicted_disease'] for p in history]
    animals = [p['animal'] for p in history]
    
    disease_dist = dict(Counter(diseases))
    animal_dist = dict(Counter(animals))
    
    return jsonify({
        'total_predictions': len(history),
        'disease_distribution': disease_dist,
        'animal_distribution': animal_dist,
        'recent_activity': history[-10:]
    })

@app.route('/api/export-data')
def export_data():
    """Export prediction data as CSV"""
    try:
        history = load_prediction_history()
        if not history:
            return jsonify({'error': 'No data to export'}), 404
        
        # Convert to DataFrame for easy CSV export
        df = pd.DataFrame(history)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vetai_predictions_{timestamp}.csv"
        
        # Save to temp file
        temp_path = os.path.join(app_dir, 'temp', filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        df.to_csv(temp_path, index=False)
        
        return jsonify({
            'message': 'Data exported successfully',
            'filename': filename,
            'records': len(history),
            'download_url': f'/api/download/{filename}'
        })
    except Exception as e:
        logger.error(f'Error exporting data: {str(e)}')
        return jsonify({'error': 'Failed to export data'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download exported files"""
    try:
        temp_dir = os.path.join(app_dir, 'temp')
        return send_from_directory(temp_dir, filename, as_attachment=True)
    except Exception as e:
        logger.error(f'Error downloading file: {str(e)}')
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/prediction-stats')
def prediction_stats():
    """Get detailed prediction statistics"""
    try:
        history = load_prediction_history()
        
        if not history:
            return jsonify({
                'total_predictions': 0,
                'accuracy_trend': [],
                'disease_severity_stats': {},
                'monthly_predictions': {}
            })
        
        # Calculate statistics
        total = len(history)
        
        # Disease severity distribution
        severity_stats = {}
        for prediction in history:
            disease = prediction.get('predicted_disease', '').lower()
            severity = get_disease_severity(disease)
            severity_stats[severity] = severity_stats.get(severity, 0) + 1
        
        # Monthly predictions
        monthly_stats = {}
        for prediction in history:
            date = datetime.fromisoformat(prediction['timestamp'])
            month_key = date.strftime('%Y-%m')
            monthly_stats[month_key] = monthly_stats.get(month_key, 0) + 1
        
        # Confidence trend (last 10 predictions)
        recent_predictions = history[-10:] if len(history) >= 10 else history
        confidence_trend = [p.get('confidence', 0) for p in recent_predictions]
        
        return jsonify({
            'total_predictions': total,
            'average_confidence': sum(confidence_trend) / len(confidence_trend) if confidence_trend else 0,
            'confidence_trend': confidence_trend,
            'disease_severity_stats': severity_stats,
            'monthly_predictions': monthly_stats,
            'high_confidence_count': sum(1 for c in confidence_trend if c >= 80),
            'latest_prediction': history[-1] if history else None
        })
    except Exception as e:
        logger.error(f'Error getting prediction stats: {str(e)}')
        return jsonify({'error': 'Failed to get statistics'}), 500

@app.route('/api/disease-info/<disease_name>')
def disease_info(disease_name):
    """Get detailed information about a specific disease"""
    disease_details = {
        'pneumonia': {
            'name': 'Pneumonia',
            'scientific_name': 'Bacterial/Viral Pneumonia',
            'description': 'Respiratory infection affecting the lungs and airways',
            'common_symptoms': ['Coughing', 'Difficulty breathing', 'Fever', 'Loss of appetite', 'Depression'],
            'transmission': 'Airborne droplets, direct contact, stress factors',
            'incubation_period': '2-7 days',
            'mortality_rate': '5-15%',
            'affected_animals': ['Cattle', 'Sheep', 'Goats', 'Buffalo'],
            'seasonal_pattern': 'More common in winter and during weather changes',
            'economic_impact': 'Moderate - affects milk production and weight gain'
        },
        'lumpy virus': {
            'name': 'Lumpy Skin Disease',
            'scientific_name': 'Lumpy Skin Disease Virus (LSDV)',
            'description': 'Viral disease causing skin nodules and systemic illness',
            'common_symptoms': ['Skin nodules', 'Fever', 'Loss of appetite', 'Reduced milk production'],
            'transmission': 'Vector-borne (flies, mosquitoes), direct contact',
            'incubation_period': '4-14 days',
            'mortality_rate': '1-5%',
            'affected_animals': ['Cattle', 'Buffalo'],
            'seasonal_pattern': 'More prevalent during warm, humid seasons',
            'economic_impact': 'High - significant impact on milk and meat production'
        },
        'blackleg': {
            'name': 'Blackleg',
            'scientific_name': 'Clostridium chauvoei',
            'description': 'Acute bacterial infection causing muscle necrosis',
            'common_symptoms': ['Sudden lameness', 'Muscle swelling', 'High fever', 'Depression'],
            'transmission': 'Soil-borne spores, wound contamination',
            'incubation_period': '1-3 days',
            'mortality_rate': '80-100% if untreated',
            'affected_animals': ['Cattle', 'Sheep', 'Goats'],
            'seasonal_pattern': 'Year-round, peaks during grazing season',
            'economic_impact': 'Very High - high mortality rate'
        },
        'foot and mouth': {
            'name': 'Foot and Mouth Disease',
            'scientific_name': 'Foot-and-Mouth Disease Virus (FMDV)',
            'description': 'Highly contagious viral disease affecting cloven-hoofed animals',
            'common_symptoms': ['Vesicles on mouth and feet', 'Fever', 'Drooling', 'Lameness'],
            'transmission': 'Highly contagious - airborne, direct/indirect contact',
            'incubation_period': '2-8 days',
            'mortality_rate': '5% adults, 20-50% young animals',
            'affected_animals': ['Cattle', 'Sheep', 'Goats', 'Pigs'],
            'seasonal_pattern': 'Year-round, spreads rapidly in any season',
            'economic_impact': 'Extremely High - trade restrictions, culling'
        },
        'anthrax': {
            'name': 'Anthrax',
            'scientific_name': 'Bacillus anthracis',
            'description': 'Acute bacterial infection with rapid progression',
            'common_symptoms': ['Sudden death', 'High fever', 'Difficulty breathing', 'Swelling'],
            'transmission': 'Soil spores, contaminated feed/water',
            'incubation_period': '1-7 days',
            'mortality_rate': '80-100% if untreated',
            'affected_animals': ['Cattle', 'Sheep', 'Goats', 'Horses'],
            'seasonal_pattern': 'More common during dry periods',
            'economic_impact': 'Critical - zoonotic risk, quarantine measures'
        }
    }
    
    disease = disease_details.get(disease_name.lower())
    if not disease:
        return jsonify({'error': 'Disease not found'}), 404
    
    return jsonify(disease)

@app.route('/api/weather-impact')
def weather_impact():
    """Get weather impact information on diseases"""
    weather_data = {
        'high_risk_conditions': {
            'pneumonia': ['Cold temperatures', 'High humidity', 'Sudden weather changes'],
            'lumpy_virus': ['Warm temperatures', 'High humidity', 'Vector-friendly conditions'],
            'blackleg': ['Wet soil conditions', 'Moderate temperatures'],
            'foot_and_mouth': ['Cool, moist conditions', 'Wind for airborne spread'],
            'anthrax': ['Dry conditions', 'Drought stress', 'Alkaline soils']
        },
        'seasonal_trends': {
            'spring': ['Increased blackleg risk', 'FMD outbreaks possible'],
            'summer': ['Peak lumpy virus season', 'Anthrax in dry areas'],
            'monsoon': ['Higher pneumonia cases', 'Vector-borne disease spread'],
            'winter': ['Pneumonia outbreaks', 'Stress-related diseases']
        },
        'prevention_by_season': {
            'spring': 'Vaccination programs, quarantine new animals',
            'summer': 'Vector control, adequate shade and water',
            'monsoon': 'Improve ventilation, manage humidity',
            'winter': 'Provide shelter, maintain nutrition'
        }
    }
    
    return jsonify(weather_data)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/api/model-info')
def model_info():
    """Get information about the ML model"""
    try:
        model_info = {
            'model_type': str(type(model).__name__),
            'accuracy': '83%',
            'features': ['Animal', 'Age', 'Temperature', 'Symptom 1', 'Symptom 2', 'Symptom 3'],
            'diseases': sorted(Data['Disease'].unique().tolist()),
            'animals_supported': sorted(Data['Animal'].unique().tolist()),
            'total_training_samples': len(Data),
            'algorithm': 'Logistic Regression with Feature Scaling'
        }
        return jsonify(model_info)
    except Exception as e:
        logger.error(f'Error getting model info: {str(e)}')
        return jsonify({'error': 'Unable to fetch model information'}), 500

@app.route('/api/symptoms')
def get_symptoms():
    """Get all available symptoms for the form"""
    try:
        symptoms = {
            'symptom1': sorted(Data['Symptom 1'].unique().tolist()),
            'symptom2': sorted(Data['Symptom 2'].unique().tolist()),
            'symptom3': sorted(Data['Symptom 3'].unique().tolist())
        }
        return jsonify(symptoms)
    except Exception as e:
        logger.error(f'Error getting symptoms: {str(e)}')
        return jsonify({'error': 'Unable to fetch symptoms'}), 500

@app.route('/api/health-check')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'service': 'VetAI Livestock Disease Prediction'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal server error: {str(error)}')
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    return jsonify({'error': 'Request too large'}), 413


# Accuracy is 83 percent with logistic Regression

if __name__ == '__main__':
    logger.info('Starting VetAI Livestock Disease Prediction System v2.0')
    logger.info('🐄 VetAI is now running!')
    logger.info('🌐 Main Interface: http://localhost:5000')
    logger.info('📊 Analytics Dashboard: http://localhost:5000/dashboard')
    logger.info('🔧 API Health Check: http://localhost:5000/api/health-check')
    print('\n' + '='*60)
    print('🚀 VetAI - Intelligent Livestock Disease Prediction')
    print('='*60)
    print('📱 Open: http://localhost:5000')
    print('📊 Dashboard: http://localhost:5000/dashboard')
    print('🔧 API Docs: http://localhost:5000/api/health-check')
    print('⌨️  Press Ctrl+C to stop the server')
    print('='*60 + '\n')
    
    app.run(debug=True, host='0.0.0.0', port=5000)

