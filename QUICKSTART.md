# 🚀 Quick Start Guide

Get up and running with the Diabetes Prediction App in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Steps

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Run the Application

**Option A: Using the main app file**
```bash
python app.py
```

**Option B: Using the run script**
```bash
python run.py
```

### 3️⃣ Access the Application

Open your browser and visit:
```
http://127.0.0.1:5000
```

## First Time Setup

The application will automatically:
- ✅ Create a sample dataset (if no CSV is provided)
- ✅ Train the machine learning model
- ✅ Save the model as `diabetes_model.pkl`
- ✅ Start the web server

This process takes about 10-15 seconds on the first run.

## Quick Test

1. Keep the default values in the form
2. Click "INITIATE ANALYSIS"
3. View the prediction results

## Training with Your Own Data

If you have your own diabetes dataset:

```bash
python train_model.py --csv your_data.csv --output my_model.pkl
```

Then update the `.env` file to use your model.

## Troubleshooting

### Port Already in Use
```bash
# Change the port in app.py or run.py
port=5001  # Instead of 5000
```

### Module Not Found
```bash
# Make sure you're in the virtual environment
pip install -r requirements.txt
```

### Model Training Failed
```bash
# Delete the old model and retrain
rm diabetes_model.pkl
python app.py
```

## Next Steps

- 📖 Read the full [README.md](README.md) for detailed documentation
- 🔧 Customize the configuration in `config/config.py`
- 🎨 Modify the UI in `templates/index.html` and `static/css/style.css`
- 🚀 Deploy to production using Gunicorn or Docker

## Need Help?

Open an issue on GitHub or check the documentation in the README.

---

**Happy Predicting! 🩺**
