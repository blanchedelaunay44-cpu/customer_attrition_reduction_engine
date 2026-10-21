import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

TRAIN_CSV = "data/train.csv"
TARGET_COL = "churn"
ARTIFACTS_DIR = "model/artifacts"

# Create artifacts directory if it doesn't exist
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def train_preprocessing():
    """Train preprocessing artifacts and save them for future use."""
    df = pd.read_csv(TRAIN_CSV)
    
    # Keep labels as strings (normalized)
    y = df[TARGET_COL].astype(str).str.strip().str.lower()
    X = df.drop(columns=[TARGET_COL])
    
    # --- NEW: decide types BEFORE the split ---
    numeric_cols = X.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_cols = [c for c in X.columns if c not in numeric_cols]
    # set category dtype on the full X so train/test share the same categories
    if categorical_cols:
        X[categorical_cols] = X[categorical_cols].astype("category")
    
    # Split
    x_train, x_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=42
    )
    
    # Scale only numeric columns (use the *names* chosen above)
    sc = StandardScaler()
    if numeric_cols:
        x_train_num = pd.DataFrame(
            sc.fit_transform(x_train[numeric_cols]),
            columns=numeric_cols, index=x_train.index
        )
        x_test_num = pd.DataFrame(
            sc.transform(x_test[numeric_cols]),
            columns=numeric_cols, index=x_test.index
        )
    else:
        x_train_num = pd.DataFrame(index=x_train.index)
        x_test_num = pd.DataFrame(index=x_test.index)
    
    # Rebuild X with scaled numerics + unscaled categoricals (still dtype=category)
    x_train = x_train_num
    x_test = x_test_num
    for col in categorical_cols:
        x_train[col] = X.loc[x_train.index, col]   # retains category dtype + categories
        x_test[col]  = X.loc[x_test.index,  col]
    
    # Save preprocessing artifacts
    artifacts = {
        'numeric_cols': numeric_cols,
        'categorical_cols': categorical_cols,
        'scaler': sc,
        'category_mappings': {}
    }
    
    # Save category mappings for each categorical column
    for col in categorical_cols:
        artifacts['category_mappings'][col] = X[col].cat.categories.tolist()
    
    # Save all artifacts to file
    with open(os.path.join(ARTIFACTS_DIR, 'preprocessing_artifacts.pkl'), 'wb') as f:
        pickle.dump(artifacts, f)
    
    print(f"Preprocessing artifacts saved to {ARTIFACTS_DIR}")
    
    return x_train, x_test, y_train, y_test

def preprocess_new_data(csv_file_path):
    """
    Preprocess new data using the same transformations as training data.
    
    Args:
        csv_file_path (str): Path to the new CSV file to preprocess
        
    Returns:
        pd.DataFrame: Preprocessed features ready for model prediction
    """
    # Load preprocessing artifacts
    with open(os.path.join(ARTIFACTS_DIR, 'preprocessing_artifacts.pkl'), 'rb') as f:
        artifacts = pickle.load(f)
    
    numeric_cols = artifacts['numeric_cols']
    categorical_cols = artifacts['categorical_cols']
    scaler = artifacts['scaler']
    category_mappings = artifacts['category_mappings']
    
    # Load new data
    df_new = pd.read_csv(csv_file_path)
    
    # Remove target column if present (in case user uploads full data)
    if TARGET_COL in df_new.columns:
        X_new = df_new.drop(columns=[TARGET_COL])
    else:
        X_new = df_new.copy()
    
    # Ensure all expected columns are present
    missing_cols = set(numeric_cols + categorical_cols) - set(X_new.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Set categorical dtypes with the same categories as training data
    for col in categorical_cols:
        if col in X_new.columns:
            X_new[col] = pd.Categorical(X_new[col], categories=category_mappings[col])
    
    # Scale numeric columns using fitted scaler
    if numeric_cols:
        X_new_num = pd.DataFrame(
            scaler.transform(X_new[numeric_cols]),
            columns=numeric_cols,
            index=X_new.index
        )
    else:
        X_new_num = pd.DataFrame(index=X_new.index)
    
    # Rebuild X with scaled numerics + categoricals
    X_processed = X_new_num.copy()
    for col in categorical_cols:
        X_processed[col] = X_new[col]
    
    return X_processed

# Train preprocessing and create variables for backward compatibility
x_train, x_test, y_train, y_test = train_preprocessing()

# Load artifacts to make them accessible
with open(os.path.join(ARTIFACTS_DIR, 'preprocessing_artifacts.pkl'), 'rb') as f:
    artifacts = pickle.load(f)

numeric_cols = artifacts['numeric_cols']
categorical_cols = artifacts['categorical_cols']
scaler = artifacts['scaler']
category_mappings = artifacts['category_mappings']

# Optional uppercase aliases
X_train, X_test = x_train, x_test
Y_train, Y_test = y_train, y_test