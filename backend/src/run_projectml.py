"""
PROJECTML (2).ipynb - Converted to Python Script
This script runs all the cells from the Jupyter notebook.
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set display options for better output
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 200)

print("="*60)
print("CELL 1: Loading and exploring data")
print("="*60)

df = pd.read_csv("stress_detection_data.csv")
print("\nFirst 5 rows:")
print(df.head())
print("\nData Info:")
print(df.info())
print("\nData Description:")
print(df.describe())

print("\n" + "="*60)
print("CELL 2: Checking missing values")
print("="*60)

print("\nMissing values count:")
print(df.isnull().sum())
print("\nMissing values percentage:")
print((df.isnull().sum() / len(df)) * 100)

print("\n" + "="*60)
print("CELL 3: Target distribution")
print("="*60)

print("\nStress Detection distribution:")
print(df["Stress_Detection"].value_counts(normalize=True) * 100)

print("\n" + "="*60)
print("CELL 4: Class balancing using resample")
print("="*60)

from sklearn.utils import resample

df_low = df[df["Stress_Detection"] == "Low"]
df_med = df[df["Stress_Detection"] == "Medium"]
df_high = df[df["Stress_Detection"] == "High"]

df_med_down = resample(df_med, replace=False, n_samples=len(df_low), random_state=42)
df_high_down = resample(df_high, replace=False, n_samples=len(df_low), random_state=42)

df_balanced = pd.concat([df_low, df_med_down, df_high_down])
print("\nBalanced dataset shape:", df_balanced.shape)
print("Balanced dataset sample:")
print(df_balanced.head())

print("\n" + "="*60)
print("CELL 5: OneHotEncoding categorical variables")
print("="*60)

from sklearn.preprocessing import OneHotEncoder

df = pd.read_csv('stress_detection_data.csv')

cat_cols = ['Gender', 'Occupation', 'Marital_Status',
            'Smoking_Habit', 'Meditation_Practice', 'Exercise_Type']

for col in cat_cols:
    df[f'{col}_original'] = df[col]

ohe = OneHotEncoder(sparse_output=False, drop=None, handle_unknown='ignore')
encoded_data = ohe.fit_transform(df[cat_cols])
encoded_cols = ohe.get_feature_names_out(cat_cols)
df_encoded = pd.DataFrame(encoded_data, columns=encoded_cols, index=df.index)

df = df.drop(columns=cat_cols)
df = pd.concat([df, df_encoded], axis=1)

print("\nOneHot Encoded features sample:")
print(df[[f'{col}_original' for col in cat_cols[:2]] + list(encoded_cols[:10])].head(5))

df.to_csv('stress_detection_data_encoded.csv', index=False)
print("\nEncoded data saved to stress_detection_data_encoded.csv")

print("\n" + "="*60)
print("CELL 6: Converting Wake_Up_Time to minutes")
print("="*60)

def time_to_minutes(t):
    if pd.isnull(t):
        return np.nan
    try:
        x = pd.to_datetime(t)
        return x.hour*60 + x.minute
    except:
        return np.nan

df['Wake_Up_Time_original'] = df['Wake_Up_Time']
df['Wake_Up_Time'] = df['Wake_Up_Time'].apply(time_to_minutes)
print("\nWake_Up_Time conversion:")
print(df[['Wake_Up_Time_original','Wake_Up_Time']].head(5))

print("\n" + "="*60)
print("CELL 7: Converting Bed_Time to minutes")
print("="*60)

df['Bed_Time_original'] = df['Bed_Time']
df['Bed_Time'] = df['Bed_Time'].apply(time_to_minutes)
print("\nBed_Time conversion:")
print(df[['Bed_Time_original','Bed_Time']].head(5))

df.to_csv('stress_detection_data_encoded.csv', index=False)

print("\n" + "="*60)
print("CELL 8: Scaling numerical features")
print("="*60)

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
numeric_cols = ['Sleep_Duration', 'Sleep_Quality', 'Physical_Activity',
                'Screen_Time', 'Caffeine_Intake', 'Alcohol_Intake',
                'Work_Hours', 'Travel_Time', 'Social_Interactions',
                'Blood_Sugar_Level', 'Cholesterol_Level']

for col in numeric_cols:
    df[f'{col}_original'] = df[col]
    df[col] = scaler.fit_transform(df[[col]])

print("\nScaled features sample:")
print(df[['Sleep_Duration', 'Sleep_Duration_original', 'Sleep_Quality', 'Sleep_Quality_original']].head())

df.to_csv('stress_detection_data_encoded.csv', index=False)

print("\n" + "="*60)
print("CELL 9: Encoding target variable")
print("="*60)

df = pd.read_csv("stress_detection_data_encoded.csv")
df['Stress_Detection_original'] = df['Stress_Detection']

print("Unique values before transformation:", df['Stress_Detection'].unique())
mapping = {'Low': 1, 'Medium': 2, 'High': 3}
df['Stress_Detection'] = df['Stress_Detection'].map(mapping)
print("Unique values after transformation:", df['Stress_Detection'].unique())

df.to_csv("stress_detection_data_encoded.csv", index=False)
print("\nTarget encoding complete.")

print("\n" + "="*60)
print("CELL 10: Removing original columns and preparing for modeling")
print("="*60)

df = pd.read_csv("stress_detection_data_encoded.csv")
df = df[[col for col in df.columns if not col.endswith("_original")]]
print("\nCleaned dataset shape:", df.shape)
print("Columns:", len(df.columns))
print(df.head())

print("\n" + "="*60)
print("CELL 11: Train-Test Split")
print("="*60)

from sklearn.model_selection import train_test_split

X = df.drop('Stress_Detection', axis=1)
y = df['Stress_Detection']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\nTraining set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")

print("\n" + "="*60)
print("CELL 12: Training Logistic Regression Model")
print("="*60)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

lr_model = LogisticRegression(max_iter=1000, random_state=42)
lr_model.fit(X_train, y_train)
y_pred_lr = lr_model.predict(X_test)
accuracy_lr = accuracy_score(y_test, y_pred_lr)
print(f"\nLogistic Regression Accuracy: {accuracy_lr * 100:.2f}%")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_lr))
print("\nClassification Report:")
print(classification_report(y_test, y_pred_lr, target_names=['Low (1)', 'Medium (2)', 'High (3)']))

print("\n" + "="*60)
print("CELL 13: Training Random Forest Model")
print("="*60)

from sklearn.ensemble import RandomForestClassifier

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)
accuracy_rf = accuracy_score(y_test, y_pred_rf)
print(f"\nRandom Forest Accuracy: {accuracy_rf * 100:.2f}%")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_rf))
print("\nClassification Report:")
print(classification_report(y_test, y_pred_rf, target_names=['Low (1)', 'Medium (2)', 'High (3)']))

print("\n" + "="*60)
print("MODEL COMPARISON SUMMARY")
print("="*60)
print(f"\nLogistic Regression Accuracy: {accuracy_lr * 100:.2f}%")
print(f"Random Forest Accuracy: {accuracy_rf * 100:.2f}%")

if accuracy_rf > accuracy_lr:
    print(f"\n[OK] Random Forest is the better model with {accuracy_rf * 100:.2f}% accuracy")
else:
    print(f"\n[OK] Logistic Regression is the better model with {accuracy_lr * 100:.2f}% accuracy")

print("\n" + "="*60)
print("FEATURE IMPORTANCE (Random Forest)")
print("="*60)

feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 15 Important Features:")
print(feature_importance.head(15).to_string(index=False))

print("\n" + "="*60)
print("SCRIPT COMPLETED SUCCESSFULLY")
print("="*60)
