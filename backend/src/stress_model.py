"""
AI-Based Stress Detection Model
================================
This module trains and evaluates ML models for stress level prediction.
Based on PROJECTML.ipynb preprocessing approach.

Features: 21 input features including lifestyle, health, and work-related factors
Target: Stress_Detection (Low / Medium / High -> 1 / 2 / 3)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.utils import resample
import joblib
import warnings
import os

warnings.filterwarnings('ignore')

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================
# 1. DATA LOADING AND EXPLORATION
# ============================================

def load_data(filepath):
    """Load the stress detection dataset"""
    df = pd.read_csv(filepath)
    print("=" * 60)
    print("DATASET INFORMATION")
    print("=" * 60)
    print(f"Total Samples: {len(df)}")
    print(f"Total Features: {len(df.columns) - 1}")
    print(f"\nFeatures: {list(df.columns[:-1])}")
    print(f"\nTarget Variable: {df.columns[-1]}")
    print(f"\nClass Distribution:")
    print(df['Stress_Detection'].value_counts())
    print(f"\nMissing Values: {df.isnull().sum().sum()}")
    return df

# ============================================
# 2. TIME CONVERSION
# ============================================

def time_to_minutes(t):
    """Convert time string (e.g., '7:00 AM') to minutes since midnight"""
    if pd.isnull(t):
        return np.nan
    try:
        x = pd.to_datetime(t)
        return x.hour * 60 + x.minute
    except:
        return np.nan

# ============================================
# 3. DATA PREPROCESSING (PROJECTML.ipynb approach)
# ============================================

def preprocess_data(df):
    """
    Preprocess the dataset using PROJECTML.ipynb approach:
    - OneHotEncoder for categorical variables
    - Time conversion for Wake_Up_Time and Bed_Time
    - StandardScaler for numerical features
    - Class balancing using resample
    """
    print("\n" + "=" * 60)
    print("DATA PREPROCESSING (PROJECTML.ipynb approach)")
    print("=" * 60)
    
    # Create a copy
    data = df.copy()
    
    # Define categorical columns for OneHotEncoder
    cat_cols = ['Gender', 'Occupation', 'Marital_Status',
                'Smoking_Habit', 'Meditation_Practice', 'Exercise_Type']
    
    # Define numerical columns for StandardScaler
    numeric_cols = ['Age', 'Sleep_Duration', 'Sleep_Quality', 'Physical_Activity',
                    'Screen_Time', 'Caffeine_Intake', 'Alcohol_Intake',
                    'Work_Hours', 'Travel_Time', 'Social_Interactions',
                    'Blood_Pressure', 'Cholesterol_Level', 'Blood_Sugar_Level']
    
    # Time columns to convert
    time_cols = ['Wake_Up_Time', 'Bed_Time']
    
    print("\n1. Converting time columns to minutes...")
    for col in time_cols:
        if col in data.columns:
            data[col] = data[col].apply(time_to_minutes)
            print(f"   - {col}: converted to minutes")
    
    # Add time columns to numeric columns
    numeric_cols.extend(time_cols)
    
    print("\n2. OneHot Encoding categorical variables...")
    # Initialize OneHotEncoder
    ohe = OneHotEncoder(sparse_output=False, drop=None, handle_unknown='ignore')
    
    # Fit and transform categorical columns
    cat_data_original = data[cat_cols]
    encoded_data = ohe.fit_transform(cat_data_original)
    encoded_cols = ohe.get_feature_names_out(cat_cols)
    
    print(f"   - Created {len(encoded_cols)} encoded features from {len(cat_cols)} categorical columns")
    
    # Create DataFrame with encoded data
    df_encoded = pd.DataFrame(encoded_data, columns=encoded_cols, index=data.index)
    
    # Remove original categorical columns and add encoded ones
    data = data.drop(columns=cat_cols)
    data = pd.concat([data, df_encoded], axis=1)
    
    print("\n3. Encoding target variable...")
    # Encode target variable (Low=1, Medium=2, High=3)
    target_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
    data['Stress_Detection'] = data['Stress_Detection'].map(target_mapping)
    print(f"   - Target classes: {target_mapping}")
    
    print("\n4. Balancing classes using resample...")
    # Separate by class
    df_low = data[data['Stress_Detection'] == 1]
    df_med = data[data['Stress_Detection'] == 2]
    df_high = data[data['Stress_Detection'] == 3]
    
    # Get the size of the smallest class
    min_class_size = min(len(df_low), len(df_med), len(df_high))
    
    # Downsample to balance
    df_low_down = resample(df_low, replace=False, n_samples=min_class_size, random_state=42)
    df_med_down = resample(df_med, replace=False, n_samples=min_class_size, random_state=42)
    df_high_down = resample(df_high, replace=False, n_samples=min_class_size, random_state=42)
    
    data_balanced = pd.concat([df_low_down, df_med_down, df_high_down])
    print(f"   - Balanced dataset: {len(data_balanced)} samples ({min_class_size} per class)")
    
    # Separate features and target
    X = data_balanced.drop('Stress_Detection', axis=1)
    y = data_balanced['Stress_Detection']
    
    print("\n5. Scaling numerical features...")
    # Scale numerical features
    scaler = StandardScaler()
    
    # Filter numeric columns that exist in X
    existing_numeric_cols = [col for col in numeric_cols if col in X.columns]
    X[existing_numeric_cols] = scaler.fit_transform(X[existing_numeric_cols])
    print(f"   - Scaled {len(existing_numeric_cols)} numerical features")
    
    print(f"\n✓ Final feature count: {len(X.columns)}")
    
    return X, y, ohe, scaler, cat_cols, existing_numeric_cols

# ============================================
# 4. MODEL TRAINING
# ============================================

def train_models(X_train, X_test, y_train, y_test):
    """
    Train and evaluate multiple ML models:
    1. Logistic Regression (from PROJECTML.ipynb)
    2. Random Forest
    3. Support Vector Machine (SVM)
    """
    print("\n" + "=" * 60)
    print("MODEL TRAINING & EVALUATION")
    print("=" * 60)
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='rbf', random_state=42, probability=True)
    }
    
    results = {}
    trained_models = {}
    
    for name, model in models.items():
        print(f"\n{'='*40}")
        print(f"Training: {name}")
        print('='*40)
        
        # Train model
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Accuracy
        accuracy = accuracy_score(y_test, y_pred)
        
        # Store results
        results[name] = {
            'accuracy': accuracy,
            'predictions': y_pred,
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'classification_report': classification_report(y_test, y_pred, 
                                                          target_names=['Low (1)', 'Medium (2)', 'High (3)'])
        }
        trained_models[name] = model
        
        print(f"Accuracy: {accuracy * 100:.2f}%")
        print(f"\nConfusion Matrix:")
        print(results[name]['confusion_matrix'])
        print(f"\nClassification Report:")
        print(results[name]['classification_report'])
    
    return trained_models, results

# ============================================
# 5. MODEL COMPARISON & SELECTION
# ============================================

def compare_models(results):
    """Compare all models and select the best one"""
    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    
    comparison = []
    for name, result in results.items():
        comparison.append({
            'Model': name,
            'Accuracy (%)': round(result['accuracy'] * 100, 2)
        })
    
    comparison_df = pd.DataFrame(comparison)
    comparison_df = comparison_df.sort_values('Accuracy (%)', ascending=False)
    print("\n" + comparison_df.to_string(index=False))
    
    best_model = comparison_df.iloc[0]['Model']
    best_accuracy = comparison_df.iloc[0]['Accuracy (%)']
    
    print(f"\n{'='*40}")
    print(f"BEST MODEL: {best_model}")
    print(f"ACCURACY: {best_accuracy}%")
    print(f"{'='*40}")
    
    return best_model, best_accuracy

# ============================================
# 6. FEATURE IMPORTANCE ANALYSIS
# ============================================

def analyze_feature_importance(model, feature_names, model_name):
    """Analyze feature importance"""
    print("\n" + "=" * 60)
    print("FEATURE IMPORTANCE (Stress Triggers)")
    print("=" * 60)
    
    if hasattr(model, 'feature_importances_'):
        # Random Forest
        importance = pd.DataFrame({
            'Feature': feature_names,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        print(f"\nTop 10 Stress Triggers ({model_name}):")
        print("-" * 40)
        for i, row in importance.head(10).iterrows():
            print(f"  {row['Feature']}: {row['Importance']*100:.2f}%")
        
        return importance
    
    elif hasattr(model, 'coef_'):
        # Logistic Regression
        coef = model.coef_
        importance = pd.DataFrame(coef, columns=feature_names).abs().mean()
        top15 = importance.sort_values(ascending=False).head(15)
        
        print(f"\nTop 15 Stress Triggers ({model_name}):")
        print("-" * 40)
        for feat, val in top15.items():
            print(f"  {feat}: {val:.4f}")
        
        return top15
    
    return None

# ============================================
# 7. SAVE MODEL
# ============================================

def save_model(model, scaler, ohe, cat_cols, numeric_cols, filepath):
    """Save the trained model and preprocessing objects"""
    model_data = {
        'model': model,
        'scaler': scaler,
        'onehot_encoder': ohe,
        'cat_cols': cat_cols,
        'numeric_cols': numeric_cols,
        'target_mapping': {'Low': 1, 'Medium': 2, 'High': 3},
        'inverse_mapping': {1: 'Low', 2: 'Medium', 3: 'High'}
    }
    joblib.dump(model_data, filepath)
    print(f"\n✓ Model saved to: {filepath}")

# ============================================
# 8. MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   AI-BASED STRESS DETECTION MODEL TRAINING")
    print("   (Using PROJECTML.ipynb preprocessing approach)")
    print("=" * 60)
    
    # Load data
    csv_path = os.path.join(SCRIPT_DIR, 'stress_detection_data.csv')
    df = load_data(csv_path)
    
    # Preprocess data
    X, y, ohe, scaler, cat_cols, numeric_cols = preprocess_data(df)
    
    # Split data (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTraining Set: {len(X_train)} samples")
    print(f"Testing Set: {len(X_test)} samples")
    
    # Train models
    trained_models, results = train_models(X_train, X_test, y_train, y_test)
    
    # Compare models
    best_model_name, best_accuracy = compare_models(results)
    
    # Feature importance analysis
    analyze_feature_importance(
        trained_models[best_model_name], 
        X.columns.tolist(),
        best_model_name
    )
    
    # Save best model
    model_path = os.path.join(SCRIPT_DIR, 'stress_model.pkl')
    save_model(
        trained_models[best_model_name],
        scaler,
        ohe,
        cat_cols,
        numeric_cols,
        model_path
    )
    
    print("\n" + "=" * 60)
    print("   MODEL TRAINING COMPLETE!")
    print("=" * 60)
    print(f"\n✓ Best Model: {best_model_name}")
    print(f"✓ Accuracy: {best_accuracy}%")
    print(f"✓ Model saved as: stress_model.pkl")
    print("\n")
