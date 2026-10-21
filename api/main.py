import os
import tempfile
import pandas as pd
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Dict, Any

# Import our model functions
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.preprocessing import preprocess_new_data
from model.train_model import load_models
from model.reasons import load_shap_explainer, compute_top_reasons_with_loaded_models
from model.business_plan import generate_business_plan

# Lifespan event handler for startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models and artifacts when the API starts."""
    print("Loading models and artifacts...")
    load_model_artifacts()
    print("Models loaded successfully!")
    yield
    print("Shutting down...")

# Initialize FastAPI app with lifespan handler
app = FastAPI(
    title="Churn Prediction API",
    description="API for customer churn prediction with explanations",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models for API responses
class PredictionResult(BaseModel):
    customer_id: str
    churn_probability: float
    churn_prediction: str
    risk_level: str

class ExplanationResult(BaseModel):
    feature: str
    importance: float
    direction: str
    suggested_action: str

class StrategicPriority(BaseModel):
    priority_level: str
    description: str
    focus_area: str
    target_driver: str
    importance_score: float
    target_impact: str

class ActionInitiative(BaseModel):
    initiative_id: str
    initiative_name: str
    target_driver: str
    phase: str
    timeline: str
    specific_actions: List[str]
    estimated_cost: int
    expected_impact: str
    implementation_complexity: str
    success_indicators: List[str]

class SuccessMetric(BaseModel):
    metric_name: str
    current_value: str
    target_value: str
    measurement_method: str
    review_frequency: str

class ResourceRequirement(BaseModel):
    total_investment: int
    resource_breakdown: Dict[str, int]
    personnel_requirements: List[str]
    technology_requirements: List[str]

class RiskMitigation(BaseModel):
    risk: str
    probability: str
    impact: str
    mitigation_strategy: str

class BusinessPlanResult(BaseModel):
    plan_metadata: Dict[str, Any]
    executive_summary: str
    strategic_priorities: List[StrategicPriority]
    action_plan: List[ActionInitiative]
    success_metrics: List[SuccessMetric]
    resource_requirements: ResourceRequirement
    risk_mitigation: List[RiskMitigation]

class ChurnAnalysisResult(BaseModel):
    success: bool
    message: str
    predictions: List[PredictionResult]
    top_reasons: List[ExplanationResult]
    summary: Dict[str, Any]
    business_plan: BusinessPlanResult

# Global variables for loaded models (loaded once at startup)
models_cache = {}
explainer_cache = {}

def load_model_artifacts():
    """Load all models and artifacts once at startup."""
    try:
        models_cache['models'] = load_models()
        models_cache['label_encoder'] = models_cache['models']['label_encoder']
        print("✅ Models loaded successfully")
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        raise

    try:
        explainer_cache['explainer'] = load_shap_explainer()
        print("✅ SHAP explainer loaded successfully")
    except Exception as e:
        print(f"❌ Error loading SHAP explainer: {e}")
        raise

def predict_churn(df_processed, models_dict):
    """Make predictions using all available models."""
    predictions = []
    
    # Helper function to convert categorical to numeric for sklearn models
    def to_numeric_for_sklearn(df):
        df_num = df.copy()
        for col in df_num.columns:
            s = df_num[col]
            if hasattr(s, "dtype") and str(s.dtype) == "category":
                codes = s.cat.codes
                df_num[col] = codes.replace({-1: codes.max() + 1}).astype("int64")
        return df_num
    
    # Get models
    xgb_model = models_dict.get('xgboost')
    rf_model = models_dict.get('random_forest') 
    catboost_model = models_dict.get('catboost')
    log_reg_model = models_dict.get('logistic_regression')
    label_encoder = models_dict['label_encoder']
    
    # Prepare data for different models
    X_num = to_numeric_for_sklearn(df_processed)
    cat_features = [c for c in df_processed.columns if str(df_processed[c].dtype) == "category"]
    
    # Collect predictions from available models
    all_probs = []
    
    if xgb_model is not None:
        probs = xgb_model.predict_proba(df_processed)[:, 1]
        all_probs.append(probs)
    
    if rf_model is not None:
        probs = rf_model.predict_proba(X_num)[:, 1]
        all_probs.append(probs)
    
    if log_reg_model is not None:
        probs = log_reg_model.predict_proba(X_num)[:, 1]
        all_probs.append(probs)
    
    if catboost_model is not None and cat_features:
        from catboost import Pool
        test_pool = Pool(df_processed, cat_features=cat_features)
        probs = catboost_model.predict_proba(test_pool)[:, 1]
        all_probs.append(probs)
    
    if not all_probs:
        raise HTTPException(status_code=500, detail="No models available for prediction")
    
    # Average predictions from all models
    avg_probs = np.mean(all_probs, axis=0)
    
    # Convert to binary predictions
    binary_preds = (avg_probs > 0.5).astype(int)
    pred_labels = label_encoder.inverse_transform(binary_preds)
    
    return avg_probs, pred_labels

def categorize_risk(probability):
    """Categorize risk level based on probability."""
    if probability >= 0.7:
        return "High"
    elif probability >= 0.4:
        return "Medium"
    else:
        return "Low"

def generate_business_plan_result(top_reasons_df, customer_summary):
    """Generate business plan result for API response."""
    business_plan = generate_business_plan(top_reasons_df, customer_summary)
    
    return BusinessPlanResult(
        plan_metadata=business_plan["plan_metadata"],
        executive_summary=business_plan["executive_summary"],
        strategic_priorities=[
            StrategicPriority(**priority) for priority in business_plan["strategic_priorities"]
        ],
        action_plan=[
            ActionInitiative(**action) for action in business_plan["action_plan"]
        ],
        success_metrics=[
            SuccessMetric(**metric) for metric in business_plan["success_metrics"]
        ],
        resource_requirements=ResourceRequirement(**business_plan["resource_requirements"]),
        risk_mitigation=[
            RiskMitigation(**risk) for risk in business_plan["risk_mitigation"]
        ]
    )



@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "Churn Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "models_loaded": len(models_cache) > 0}

@app.post("/upload", response_model=ChurnAnalysisResult)
async def upload_and_predict(file: UploadFile = File(...)):
    """
    Upload a CSV file and get churn predictions with explanations.
    
    - **file**: CSV file with customer data (same format as training data)
    - **returns**: Predictions, top churn reasons, and suggested actions
    """
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Process the uploaded file
        df_processed = preprocess_new_data(tmp_file_path)
        
        # Make predictions
        probabilities, predictions = predict_churn(df_processed, models_cache['models'])
        
        # Create prediction results
        prediction_results = []
        for i, (prob, pred) in enumerate(zip(probabilities, predictions)):
            prediction_results.append(PredictionResult(
                customer_id=f"Customer_{i+1}",
                churn_probability=float(prob),
                churn_prediction=str(pred),
                risk_level=categorize_risk(float(prob))
            ))
        
        # Get top reasons (using original training data for consistency)
        top_reasons_df = compute_top_reasons_with_loaded_models(top_n=5)
        explanation_results = []
        for _, row in top_reasons_df.iterrows():
            explanation_results.append(ExplanationResult(
                feature=str(row['feature']),
                importance=float(row['importance']),
                direction=str(row['direction']),
                suggested_action=str(row['suggested_action'])
            ))
        
        # Create summary
        total_customers = len(probabilities)
        churn_risk_customers = sum(1 for pred in predictions if pred == 'yes')
        avg_risk_probability = float(np.mean(probabilities))
        
        summary = {
            "total_customers": total_customers,
            "customers_at_risk": churn_risk_customers,
            "churn_rate": round(churn_risk_customers / total_customers * 100, 2),
            "average_risk_probability": round(avg_risk_probability, 3),
            "high_risk_customers": sum(1 for prob in probabilities if prob >= 0.7),
            "medium_risk_customers": sum(1 for prob in probabilities if 0.4 <= prob < 0.7),
            "low_risk_customers": sum(1 for prob in probabilities if prob < 0.4)
        }
        
        # Generate comprehensive business plan
        business_plan_result = generate_business_plan_result(top_reasons_df, summary)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return ChurnAnalysisResult(
            success=True,
            message=f"Successfully analyzed {total_customers} customers",
            predictions=prediction_results,
            top_reasons=explanation_results,
            summary=summary,
            business_plan=business_plan_result
        )
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/model-info")
async def model_info():
    """Get information about loaded models."""
    models_dict = models_cache['models']
    
    return {
        "models_loaded": {
            "xgboost": models_dict.get('xgboost') is not None,
            "random_forest": models_dict.get('random_forest') is not None,
            "catboost": models_dict.get('catboost') is not None,
            "logistic_regression": models_dict.get('logistic_regression') is not None
        },
        "feature_names": models_dict['feature_names'],
        "categorical_features": models_dict['cat_features'],
        "total_features": len(models_dict['feature_names'])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)