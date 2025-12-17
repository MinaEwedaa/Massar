"""Train Linear Regression model on cleaned_transport_dataset.csv"""

import os
import sys
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def extract_route_number(route_id: str) -> int:
    """Extract numeric part from route_id (e.g., 'R3' -> 3)."""
    try:
        # Remove 'R' prefix and convert to int
        return int(route_id.replace('R', '').strip())
    except (ValueError, AttributeError):
        return 0

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare features for training."""
    # Create a copy to avoid modifying original
    df = df.copy()
    
    # Extract route number
    df['route_num'] = df['route_id'].apply(extract_route_number)
    
    # Select features for training
    feature_columns = [
        'hour',
        'day_of_week',
        'is_weekend',
        'weather_severity',
        'route_frequency',
        'passenger_count',
        'latitude',
        'longitude',
        'route_num'
    ]
    
    # Handle time_of_day as categorical (one-hot encode)
    time_of_day_dummies = pd.get_dummies(df['time_of_day'], prefix='time_of_day')
    
    # Combine features
    features = df[feature_columns].copy()
    features = pd.concat([features, time_of_day_dummies], axis=1)
    
    return features

def main():
    """Main training function."""
    # Paths
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cleaned_transport_dataset.csv')
    model_dir = os.path.join(os.path.dirname(__file__), 'model')
    model_path = os.path.join(model_dir, 'model.joblib')
    
    print(f"Loading dataset from: {dataset_path}")
    
    # Load dataset
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        sys.exit(1)
    
    df = pd.read_csv(dataset_path)
    print(f"Loaded {len(df)} records")
    
    # Prepare features and target
    X = prepare_features(df)
    y = df['delay_minutes']
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Feature columns: {list(X.columns)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train Linear Regression model
    print("\nTraining Linear Regression model...")
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    train_rmse = mean_squared_error(y_train, y_train_pred, squared=False)
    test_rmse = mean_squared_error(y_test, y_test_pred, squared=False)
    train_mae = mean_absolute_error(y_train, y_train_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    
    print("\n" + "="*50)
    print("MODEL PERFORMANCE METRICS")
    print("="*50)
    print(f"Training RMSE: {train_rmse:.2f} minutes")
    print(f"Test RMSE: {test_rmse:.2f} minutes")
    print(f"Training MAE: {train_mae:.2f} minutes")
    print(f"Test MAE: {test_mae:.2f} minutes")
    print(f"Training R²: {train_r2:.4f}")
    print(f"Test R²: {test_r2:.4f}")
    print("="*50)
    
    # Save model
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Print feature importance (coefficients)
    print("\nFeature Coefficients:")
    print("-" * 50)
    feature_names = list(X.columns)
    coefficients = model.coef_
    for name, coef in zip(feature_names, coefficients):
        print(f"{name:30s}: {coef:10.4f}")
    print(f"{'Intercept':30s}: {model.intercept_:10.4f}")
    
    print("\nTraining completed successfully!")

if __name__ == "__main__":
    main()

