# Customer Attrition Reduction Engine (CARE)

Hey there! This is an end-to-end churn prediction project we built as a team to help identify at-risk customers before they leave, explain *why* they might churn using SHAP values, and suggest concrete retention actions.

Instead of just leaving the trained model inside a notebook, we turned it into a full app:
- A Python backend that serves real-time predictions and explanations through an API.
- A simple web dashboard where you can test single customers or upload a full CSV batch to see risk scores immediately.

## Tech Stack

- **Machine Learning**: CatBoost, XGBoost, Scikit-learn, SHAP, Pandas, NumPy
- **Backend / API**: Python 3.12, FastAPI / Flask, Uvicorn
- **Frontend**: Plain HTML, CSS, JavaScript (Fetch API)

## What’s in the Project?

Here is an overview of how the folders are set up:

- `api/` – The backend API routes and schemas that handle incoming prediction requests.
- `data/` – The datasets used for training, plus sample test CSVs you can use to test the app right away.
- `frontend/` – The web interface (`index.html`, styles, and JS) that connects to the local API.
- `model/` – All the ML logic:
  - `preprocessing.py` – Data cleaning and feature encoding.
  - `train_model.py` – Training loops and parameter tuning.
  - `predict.py` – Prediction helpers for single and batch records.
  - `reasons.py` – Extracts the top churn reasons for each customer using SHAP.
  - `artifacts/` – Saved model weights (`.pkl`) so you don't need to retrain to run the app.
- `start_api.py` – Quick script to launch the backend API.
- `test_api.py` & `test_complete_system.py` – Test scripts to make sure endpoints and inferences work properly.

## How to Run It Locally

### 1. Setup Your Environment

First, clone the repo and set up a virtual environment so dependencies don't clash with your global Python:

```bash
git clone https://github.com/blanchedelaunay44-cpu/customer_attrition_reduction_engine.git
cd customer_attrition_reduction_engine

# Create virtual environment
python -m venv venv

# Activate it:
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Mac/Linux:
source venv/bin/activate

# Install the packages:
pip install -r api_requirements.txt
```

### 2. Start the Backend API

In your project root, run:

```bash
python start_api.py
```

The API will run locally at `http://127.0.0.1:8000`. You can also check out the interactive documentation at `http://127.0.0.1:8000/docs`.

### 3. Launch the Web Interface

Open a **new terminal tab or window**, go into the `frontend/` folder, and spin up a lightweight server:

```bash
cd frontend
python -m http.server 3000
```

Now open your browser and head to:
```text
http://localhost:3000
```

## Testing the App with Sample Data

You don't need to invent customer numbers or prepare a dataset to test the website. We included ready-to-use CSV files inside the `data/` folder:

- `data/test_upload.csv` – A small, clean file to test a quick upload.
- `data/test1_customers_upsampled_200.csv` – A larger batch of 200 customers if you want to see how the dashboard handles volume.
- `data/test3_highrisk.csv` – A list of profiles with high churn risk, great for seeing the SHAP explanation triggers and recommended actions.

### How to try it:
1. Make sure both your API terminal (`port 8000`) and frontend terminal (`port 3000`) are running.
2. Go to `http://localhost:3000` in your browser.
3. In the upload section, click **Browse / Choose File** and pick one of the sample CSV files from the `data/` folder (like `test_upload.csv`).
4. Hit **Analyze / Predict**.
5. The dashboard will show:
   - Each customer's churn risk percentage.
   - Their risk category (Low, Medium, High).
   - The primary factors driving that risk.
   - Suggested retention steps.

## Running the Tests

To verify everything is working under the hood:

```bash
# Test API endpoints
python test_api.py

# Test the full end-to-end flow
python test_complete_system.py
```
