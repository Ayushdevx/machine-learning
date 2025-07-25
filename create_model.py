"""
VetAI Model Recreator - Creates a compatible model for demonstration
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle
import os

class VetAIModel:
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

def create_model():
    # Load the data
    data_path = 'Cleaned_Disease_Data.csv'
    if not os.path.exists(data_path):
        print("Error: Cleaned_Disease_Data.csv not found!")
        return None
    
    # Read the data
    data = pd.read_csv(data_path)
    print(f"Loaded dataset with {len(data)} records")
    print(f"Columns: {list(data.columns)}")
    print(f"Diseases: {data['Disease'].unique()}")
    print(f"Animals: {data['Animal'].unique()}")
    
    # Prepare features and target
    features = ['Animal', 'Age', 'Temperature', 'Symptom 1', 'Symptom 2', 'Symptom 3']
    X = data[features].copy()
    y = data['Disease'].copy()
    
    # Encode categorical variables
    label_encoders = {}
    categorical_columns = ['Animal', 'Symptom 1', 'Symptom 2', 'Symptom 3']
    
    for col in categorical_columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le
    
    # Encode target variable
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(y)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create and train the model
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train, y_train)
    
    # Calculate accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.3f}")
    
    # Create the wrapper model
    vetai_model = VetAIModel(model, label_encoders, target_encoder, features)
    
    # Save the model
    with open('livestock_logistic_Model.pkl', 'wb') as f:
        pickle.dump(vetai_model, f)
    
    print("✅ Successfully created and saved VetAI model!")
    print("Model file: livestock_logistic_Model.pkl")
    
    return vetai_model

if __name__ == "__main__":
    model = create_model()
    
    if model:
        # Test the model
        print("\n🧪 Testing the model...")
        test_input = pd.DataFrame({
            'Animal': ['cow'],
            'Age': [5],
            'Temperature': [102.5],
            'Symptom 1': ['depression'],
            'Symptom 2': ['loss of appetite'],
            'Symptom 3': ['painless lumps']
        })
        
        prediction = model.predict(test_input)
        probabilities = model.predict_proba(test_input)
        confidence = np.max(probabilities) * 100
        
        print(f"Test prediction: {prediction[0]}")
        print(f"Confidence: {confidence:.1f}%")
        print("✅ Model is working correctly!")
