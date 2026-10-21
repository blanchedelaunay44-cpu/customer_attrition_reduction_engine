
import numpy as np
import pandas as pd
import pickle
import os
import shap
from typing import List, Tuple

from model.train_model import xgb_best, LABEL_ENCODER as label_enc, y_train_enc, load_models
from model.preprocessing import x_train, y_train

def _cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = a.size, b.size
    if na < 2 or nb < 2:
        return 0.0
    pa, pb = a.mean(), b.mean()
    sa, sb = a.std(ddof=1), b.std(ddof=1)
    s = np.sqrt(((na-1)*sa**2 + (nb-1)*sb**2) / (na + nb - 2))
    if s == 0:
        return 0.0
    return (pa - pb) / s

def _suggest_action(feature: str, direction: str) -> str:
    f = feature.lower()
    if "tenure" in f or "month" in f or "age" in f:
        return "Onboard & retain newer customers; strengthen early-life touchpoints."
    if "service" in f or "support" in f or "complaint" in f or "calls" in f:
        return "Proactive support for at-risk users; reduce friction in help channels."
    if "charge" in f or "price" in f or "cost" in f or "fee" in f or "bill" in f:
        return "Review pricing/discounts; offer plan optimization for high spenders."
    if "plan" in f or "contract" in f or "international" in f:
        return "Re-evaluate plan fit and add-ons; communicate alternatives."
    if "data" in f or "minutes" in f or "usage" in f:
        return "Offer right-sized plans; target over/under-utilizers with offers."
    if direction == "higher_risk":
        return "Investigate high values; mitigate by optimizing price/experience."
    else:
        return "Customers with higher values retain; amplify this driver (loyalty, perks)."

def compute_top_reasons(top_n: int = 5) -> pd.DataFrame:
    explainer = shap.TreeExplainer(xgb_best)
    shap_vals = explainer.shap_values(x_train)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]

    feature_names = list(x_train.columns)
    shap_vals = np.asarray(shap_vals, dtype=float)
    mean_abs = np.abs(shap_vals).mean(axis=0)
    importance = mean_abs / (mean_abs.sum() + 1e-12)

    churn_mask = (y_train_enc == 1)
    mean_shap_churn = shap_vals[churn_mask].mean(axis=0) if churn_mask.any() else np.zeros_like(importance)
    direction = np.where(mean_shap_churn >= 0, "higher_risk", "lower_risk")

    rows = []
    for j, name in enumerate(feature_names):
        col = x_train[name]
        if str(col.dtype) == "category":
            codes = col.cat.codes.values
            eff = _cohen_d(codes[churn_mask], codes[~churn_mask])
            df_tmp = pd.DataFrame({"lvl": col.astype(str).values, "y": y_train_enc})
            rate = df_tmp.groupby("lvl")["y"].mean().sort_values(ascending=False)
            worst_level = rate.index[0] if len(rate) else ""
            note = f"Highest churn at level: {worst_level}"
            churner_stat = df_tmp.loc[churn_mask, "lvl"].mode().iloc[0] if churn_mask.any() else ""
            nonchurn_stat = df_tmp.loc[~churn_mask, "lvl"].mode().iloc[0] if (~churn_mask).any() else ""
        else:
            churner_stat = np.nanmean(col.values[churn_mask].astype(float))
            nonchurn_stat = np.nanmean(col.values[~churn_mask].astype(float))
            eff = _cohen_d(col.values[churn_mask], col.values[~churn_mask])
            note = ""
        rows.append({
            "feature": name,
            "importance": importance[j],
            "direction": direction[j],
            "churners_stat": churner_stat,
            "nonchurners_stat": nonchurn_stat,
            "effect_size": eff,
            "note": note,
            "suggested_action": _suggest_action(name, direction[j])
        })

    df = pd.DataFrame(rows).sort_values("importance", ascending=False).reset_index(drop=True)
    return df.head(top_n)

def save_shap_explainer():
    """Save the SHAP explainer for later use."""
    # Load models to get the trained XGBoost
    models_dict = load_models()
    xgb_model = models_dict['xgboost']
    
    # Create and save SHAP explainer
    explainer = shap.TreeExplainer(xgb_model)
    
    explainer_path = os.path.join(os.path.dirname(__file__), 'artifacts', 'shap_explainer.pkl')
    with open(explainer_path, 'wb') as f:
        pickle.dump(explainer, f)
    
    print(f"✅ SHAP explainer saved to {explainer_path}")
    return explainer_path

def load_shap_explainer():
    """Load the saved SHAP explainer."""
    explainer_path = os.path.join(os.path.dirname(__file__), 'artifacts', 'shap_explainer.pkl')
    
    if not os.path.exists(explainer_path):
        raise FileNotFoundError(f"SHAP explainer not found at {explainer_path}. Please train models first.")
    
    with open(explainer_path, 'rb') as f:
        explainer = pickle.load(f)
    
    print(f"✅ SHAP explainer loaded from {explainer_path}")
    return explainer

def compute_top_reasons_with_loaded_models(top_n: int = 5) -> pd.DataFrame:
    """Compute top reasons using loaded models and explainer."""
    # Load models and explainer
    models_dict = load_models()
    explainer = load_shap_explainer()
    
    xgb_model = models_dict['xgboost']
    label_encoder = models_dict['label_encoder']
    y_train_enc = label_encoder.fit_transform(y_train)
    
    shap_vals = explainer.shap_values(x_train)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]

    feature_names = models_dict['feature_names']
    shap_vals = np.asarray(shap_vals, dtype=float)
    mean_abs = np.abs(shap_vals).mean(axis=0)
    importance = mean_abs / (mean_abs.sum() + 1e-12)

    churn_mask = (y_train_enc == 1)
    mean_shap_churn = shap_vals[churn_mask].mean(axis=0) if churn_mask.any() else np.zeros_like(importance)
    direction = np.where(mean_shap_churn >= 0, "higher_risk", "lower_risk")

    rows = []
    for j, name in enumerate(feature_names):
        col = x_train[name]
        if str(col.dtype) == "category":
            codes = col.cat.codes.values
            eff = _cohen_d(codes[churn_mask], codes[~churn_mask])
            df_tmp = pd.DataFrame({"lvl": col.astype(str).values, "y": y_train_enc})
            rate = df_tmp.groupby("lvl")["y"].mean().sort_values(ascending=False)
            worst_level = rate.index[0] if len(rate) else ""
            note = f"Highest churn at level: {worst_level}"
            churner_stat = df_tmp.loc[churn_mask, "lvl"].mode().iloc[0] if churn_mask.any() else ""
            nonchurn_stat = df_tmp.loc[~churn_mask, "lvl"].mode().iloc[0] if (~churn_mask).any() else ""
        else:
            churner_stat = np.nanmean(col.values[churn_mask].astype(float))
            nonchurn_stat = np.nanmean(col.values[~churn_mask].astype(float))
            eff = _cohen_d(col.values[churn_mask], col.values[~churn_mask])
            note = ""
        rows.append({
            "feature": name,
            "importance": importance[j],
            "direction": direction[j],
            "churners_stat": churner_stat,
            "nonchurners_stat": nonchurn_stat,
            "effect_size": eff,
            "note": note,
            "suggested_action": _suggest_action(name, direction[j])
        })

    df = pd.DataFrame(rows).sort_values("importance", ascending=False).reset_index(drop=True)
    return df.head(top_n)

def save_top_reasons(path: str = "data/top_reasons.csv", top_n: int = 5) -> pd.DataFrame:
    df = compute_top_reasons_with_loaded_models(top_n=top_n)
    df.to_csv(path, index=False)
    return df
