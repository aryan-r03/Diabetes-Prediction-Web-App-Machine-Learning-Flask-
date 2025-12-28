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
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_names = None

    def create_sample_dataset(self):
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
        print(f"\nLoading dataset from: {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            print(f"✓ Dataset loaded: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")

            # Check for outcome column
            if 'Outcome' in df.columns:
                df = df.rename(columns={'Outcome': 'outcome'})

            return df
        except:
            print("CSV file not found. Using sample dataset.")
            return self.create_sample_dataset()

    def train(self, df):
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

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"\nTraining samples: {len(X_train)}")
        print(f"Testing samples: {len(X_test)}")

        print("\nScaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        print("Training Random Forest model...")
        self.model.fit(X_train_scaled, y_train)

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
        try:
            features_df = pd.DataFrame([features_dict])[self.feature_names]
            features_scaled = self.scaler.transform(features_df)

            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0]

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
            return {'error': str(e), 'result': 'ERROR', 'confidence': 0,
                    'diabetes_probability': 0, 'no_diabetes_probability': 0,
                    'risk_level': 'UNKNOWN'}

    def save_model(self, filepath='diabetes_model.pkl'):
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names
            }, f)
        print(f"\n✓ Model saved to {filepath}")

    def load_model(self, filepath='diabetes_model.pkl'):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data['feature_names']
        print(f"✓ Model loaded from {filepath}")


def train_and_save_model(csv_path=None):
    diabetes_model = DiabetesModel()
    df = diabetes_model.load_dataset_from_csv(csv_path) if csv_path else diabetes_model.create_sample_dataset()
    diabetes_model.train(df)
    diabetes_model.save_model('diabetes_model.pkl')
    return diabetes_model


from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

CSV_FILE = 'diabetes.csv'

if os.path.exists('diabetes_model.pkl'):
    diabetes_analyzer = DiabetesModel()
    diabetes_analyzer.load_model('diabetes_model.pkl')
else:
    diabetes_analyzer = train_and_save_model(csv_path=CSV_FILE if os.path.exists(CSV_FILE) else None)


@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/predict', methods=['POST'])
def predict_diabetes():
    try:
        data = request.get_json()
        features = data.get('features', {})
        if not features:
            return jsonify({'error': 'No features provided'}), 400
        result = diabetes_analyzer.predict(features)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Diabetes Detection</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a3a52 0%, #2d5a6f 100%);
            min-height: 100vh;
            padding: 20px;
            color: white;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 32px;
            color: #4dd4d4;
            margin-bottom: 10px;
            font-weight: 700;
            letter-spacing: 1px;
        }

        .main-content {
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 20px;
            align-items: start;
        }

        .left-panel {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .heart-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 40px;
            box-shadow: 0 8px 25px rgba(255, 107, 157, 0.4);
            cursor: pointer;
            transition: transform 0.3s;
        }

        .heart-icon:hover {
            transform: scale(1.1);
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #4dd4d4;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-group input {
            width: 100%;
            padding: 12px 15px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(77, 212, 212, 0.3);
            border-radius: 8px;
            color: white;
            font-size: 16px;
            transition: all 0.3s;
        }

        .form-group input:focus {
            outline: none;
            background: rgba(255, 255, 255, 0.12);
            border-color: #4dd4d4;
            box-shadow: 0 0 0 3px rgba(77, 212, 212, 0.1);
        }

        .analyze-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.4);
        }

        .analyze-btn:disabled {
            background: rgba(255, 255, 255, 0.2);
            cursor: not-allowed;
            transform: none;
        }

        .right-panel {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 40px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            min-height: 600px;
            display: flex;
            flex-direction: column;
        }

        .result-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
        }

        .result-icon {
            width: 120px;
            height: 120px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 70px;
            margin-bottom: 30px;
            animation: scaleIn 0.5s;
        }

        .result-icon.success {
            background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
            box-shadow: 0 10px 40px rgba(0, 255, 136, 0.4);
        }

        .result-icon.error {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            box-shadow: 0 10px 40px rgba(255, 107, 107, 0.4);
        }

        @keyframes scaleIn {
            from {
                transform: scale(0);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }

        .result-title {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 15px;
            letter-spacing: 2px;
            text-align: center;
        }

        .result-title.success {
            color: #00ff88;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
        }

        .result-title.error {
            color: #ff6b6b;
            text-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
        }

        .risk-badge {
            display: inline-block;
            padding: 10px 25px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 35px;
            text-transform: uppercase;
            letter-spacing: 1px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.3);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            width: 100%;
            margin-top: auto;
        }

        .stat-box {
            background: rgba(26, 58, 82, 0.5);
            border: 1px solid rgba(77, 212, 212, 0.2);
            border-radius: 12px;
            padding: 25px 20px;
            text-align: center;
        }

        .stat-label {
            color: #8bb9cc;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        .stat-value {
            font-size: 36px;
            font-weight: 800;
            color: white;
        }

        .stat-value.red {
            color: #ff6b6b;
        }

        .stat-value.green {
            color: #00ff88;
        }

        .info-box {
            background: rgba(77, 212, 212, 0.1);
            border-left: 4px solid #4dd4d4;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }

        .info-box-title {
            color: #4dd4d4;
            font-weight: 700;
            font-size: 14px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .info-box-text {
            color: #8bb9cc;
            font-size: 13px;
            line-height: 1.6;
        }

        .loading {
            text-align: center;
            padding: 60px;
        }

        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid #4dd4d4;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto 25px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            color: #8bb9cc;
            font-size: 16px;
        }

        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩺 AI DIABETES DETECTION</h1>
        </div>

        <div class="main-content">
            <div class="left-panel">
                <div class="heart-icon">❤️</div>

                <form id="diabetesForm">
                    <div class="form-group">
                        <label>Pregnancies</label>
                        <input type="number" id="pregnancies" min="0" max="17" value="1" required>
                    </div>

                    <div class="form-group">
                        <label>Glucose (mg/dL)</label>
                        <input type="number" id="glucose" min="0" max="200" value="85" required>
                    </div>

                    <div class="form-group">
                        <label>Blood Pressure</label>
                        <input type="number" id="blood_pressure" min="0" max="122" value="66" required>
                    </div>

                    <div class="form-group">
                        <label>Skin Thickness</label>
                        <input type="number" id="skin_thickness" min="0" max="99" value="29" required>
                    </div>

                    <div class="form-group">
                        <label>Insulin</label>
                        <input type="number" id="insulin" min="0" max="846" value="0" required>
                    </div>

                    <div class="form-group">
                        <label>BMI</label>
                        <input type="number" id="bmi" step="0.1" min="0" max="67" value="26.6" required>
                    </div>

                    <div class="form-group">
                        <label>Diabetes Pedigree</label>
                        <input type="number" id="diabetes_pedigree" step="0.001" min="0" max="2.5" value="0.351" required>
                    </div>

                    <div class="form-group">
                        <label>Age</label>
                        <input type="number" id="age" min="21" max="81" value="31" required>
                    </div>

                    <button type="submit" class="analyze-btn" id="analyzeBtn">
                        🔬 INITIATE ANALYSIS
                    </button>
                </form>
            </div>

            <div class="right-panel">
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    <div class="loading-text">Analyzing health parameters...</div>
                </div>

                <div id="result" style="display: none;"></div>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('diabetesForm');
        const loading = document.getElementById('loading');
        const resultDiv = document.getElementById('result');
        const analyzeBtn = document.getElementById('analyzeBtn');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const features = {
                pregnancies: parseInt(document.getElementById('pregnancies').value),
                glucose: parseInt(document.getElementById('glucose').value),
                blood_pressure: parseInt(document.getElementById('blood_pressure').value),
                skin_thickness: parseInt(document.getElementById('skin_thickness').value),
                insulin: parseInt(document.getElementById('insulin').value),
                bmi: parseFloat(document.getElementById('bmi').value),
                diabetes_pedigree: parseFloat(document.getElementById('diabetes_pedigree').value),
                age: parseInt(document.getElementById('age').value)
            };

            analyzeBtn.disabled = true;
            loading.style.display = 'flex';
            resultDiv.style.display = 'none';

            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ features: features })
                });

                const data = await response.json();

                if (data.success) {
                    displayResult(data.result);
                } else {
                    displayError(data.error || 'Unknown error');
                }
            } catch (error) {
                displayError(error.message);
            } finally {
                analyzeBtn.disabled = false;
                loading.style.display = 'none';
            }
        });

        function displayResult(result) {
            const isDiabetic = result.result === 'DIABETES DETECTED';
            const isError = result.result === 'ERROR';

            if (isError) {
                displayError(result.error || 'Analysis failed');
                return;
            }

            const iconClass = isDiabetic ? 'error' : 'success';
            const titleClass = isDiabetic ? 'error' : 'success';
            const icon = isDiabetic ? '⚠️' : '✓';

            resultDiv.innerHTML = `
                <div class="result-container">
                    <div class="result-icon ${iconClass}">${icon}</div>
                    <div class="result-title ${titleClass}">${result.result}</div>
                    <div class="risk-badge">${result.risk_level}</div>

                    <div class="stats-grid">
                        <div class="stat-box">
                            <div class="stat-label">CONFIDENCE</div>
                            <div class="stat-value">${Math.round(result.confidence)}%</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">DIABETES RISK</div>
                            <div class="stat-value red">${Math.round(result.diabetes_probability)}%</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">HEALTHY</div>
                            <div class="stat-value green">${Math.round(result.no_diabetes_probability)}%</div>
                        </div>
                    </div>

                    
                </div>
            `;

            resultDiv.style.display = 'flex';
        }

        function displayError(errorMessage) {
            resultDiv.innerHTML = `
                <div class="result-container">
                    <div class="result-icon error">✓</div>
                    <div class="result-title error">ERROR</div>
                    <div class="risk-badge">UNKNOWN</div>

                    <div class="stats-grid">
                        <div class="stat-box">
                            <div class="stat-label">CONFIDENCE</div>
                            <div class="stat-value">0%</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">DIABETES RISK</div>
                            <div class="stat-value red">0%</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">HEALTHY</div>
                            <div class="stat-value green">0%</div>
                        </div>
                    </div>

                    <div class="info-box">
                        <div class="info-box-title">ℹ️ Important Information</div>
                        <div class="info-box-text">
                            This AI analysis is for screening purposes only. Missing values were automatically estimated using advanced statistical methods. For accurate diagnosis, please consult with a healthcare professional and undergo proper medical testing.
                        </div>
                    </div>
                </div>
            `;

            resultDiv.style.display = 'flex';
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Flask server...")
    print("\nOpen your browser: http://127.0.0.1:5000")

    app.run(debug=True, port=5000)