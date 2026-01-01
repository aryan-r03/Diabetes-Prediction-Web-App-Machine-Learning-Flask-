"""
Diabetes Prediction Model
Handles model training, evaluation, and prediction logic
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import warnings

warnings.filterwarnings('ignore')


class DiabetesModel:
    """
    Machine Learning model for diabetes prediction
    Uses Random Forest Classifier with feature scaling
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_names = None

    def create_sample_dataset(self):
        """
        Creates a synthetic diabetes dataset for demonstration
        Returns: pandas DataFrame with features and outcome
        """
        print("\nCreating sample diabetes dataset...")
        np.random.seed(42)
        n_samples = 1000

        data = {
            'pregnancies': np.random.randint(0, 17, n_samples),
            'glucose': np.random.randint(0, 200, n_samples),
            'blood_pressure': np.random.randint(0, 122, n_samples),
            'skin_thickness': np.random.randint(0, 99, n_samples),
            'insulin': np.random.randint(0, 846, n_samples),
            'bmi': np.random.uniform(0, 67.1, n_samples),
            'diabetes_pedigree': np.random.uniform(0.078, 2.42, n_samples),
            'age': np.random.randint(21, 81, n_samples),
        }

        df = pd.DataFrame(data)

        # Create risk-based outcome
        df['risk_score'] = (
                (df['glucose'] > 140) * 3 +
                (df['bmi'] > 30) * 2 +
                (df['age'] > 45) * 1.5 +
                (df['blood_pressure'] > 80) * 1 +
                (df['insulin'] > 166) * 1 +
                df['diabetes_pedigree'] * 2
        )

        df['outcome'] = (df['risk_score'] > df['risk_score'].median()).astype(int)
        df = df.drop('risk_score', axis=1)

        return df

    def load_dataset_from_csv(self, csv_path):
        """
        Load diabetes dataset from CSV file
        Args:
            csv_path: Path to the CSV file
        Returns: pandas DataFrame
        """
        print(f"\nLoading dataset from: {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            print(f"✓ Dataset loaded: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")

            # Normalize column names
            if 'Outcome' in df.columns:
                df = df.rename(columns={'Outcome': 'outcome'})

            return df
        except Exception as e:
            print(f"Error loading CSV: {e}")
            print("Using sample dataset instead.")
            return self.create_sample_dataset()

    def train(self, df):
        """
        Train the diabetes prediction model
        Args:
            df: pandas DataFrame with features and outcome
        Returns: accuracy score
        """
        print("\n" + "=" * 60)
        print("TRAINING DIABETES DETECTION MODEL")
        print("=" * 60)

        X = df.drop('outcome', axis=1)
        y = df['outcome']
        self.feature_names = X.columns.tolist()

        print(f"\nDataset size: {len(df)}")
        print(f"Features: {len(X.columns)}")
        print(f"Diabetic: {(y == 1).sum()} ({(y == 1).sum() / len(y) * 100:.1f}%)")
        print(f"Non-Diabetic: {(y == 0).sum()} ({(y == 0).sum() / len(y) * 100:.1f}%)")

        # Split dataset
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"\nTraining samples: {len(X_train)}")
        print(f"Testing samples: {len(X_test)}")

        # Scale features
        print("\nScaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        print("Training Random Forest model...")
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)

        print("\n" + "=" * 60)
        print("MODEL EVALUATION RESULTS")
        print("=" * 60)
        print(f"Accuracy: {accuracy * 100:.2f}%")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred,
                                    target_names=['No Diabetes', 'Diabetes']))

        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"True Negatives:  {cm[0][0]}")
        print(f"False Positives: {cm[0][1]}")
        print(f"False Negatives: {cm[1][0]}")
        print(f"True Positives:  {cm[1][1]}")

        return accuracy

    def predict(self, features_dict):
        """
        Make a prediction for given features
        Args:
            features_dict: Dictionary containing feature values
        Returns: Dictionary with prediction results
        """
        try:
            # Create DataFrame with correct feature order
            features_df = pd.DataFrame([features_dict])[self.feature_names]
            features_scaled = self.scaler.transform(features_df)

            # Predict
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0]

            # Determine result and risk level
            result = "DIABETES DETECTED" if prediction == 1 else "NO DIABETES"
            confidence = max(probability) * 100

            diabetes_prob = probability[1] * 100
            if diabetes_prob < 30:
                risk_level = "LOW RISK"
            elif diabetes_prob < 60:
                risk_level = "MODERATE RISK"
            else:
                risk_level = "HIGH RISK"

            return {
                'result': result,
                'confidence': round(confidence, 2),
                'diabetes_probability': round(probability[1] * 100, 2),
                'no_diabetes_probability': round(probability[0] * 100, 2),
                'risk_level': risk_level,
                'prediction': int(prediction)
            }
        except Exception as e:
            return {
                'error': str(e),
                'result': 'ERROR',
                'confidence': 0,
                'diabetes_probability': 0,
                'no_diabetes_probability': 0,
                'risk_level': 'UNKNOWN'
            }

    def save_model(self, filepath='diabetes_model.pkl'):
        """
        Save trained model to disk
        Args:
            filepath: Path where model should be saved
        """
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names
            }, f)
        print(f"\n✓ Model saved to {filepath}")

    def load_model(self, filepath='diabetes_model.pkl'):
        """
        Load trained model from disk
        Args:
            filepath: Path to saved model
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data['feature_names']
        print(f"✓ Model loaded from {filepath}")
