"""Check what features the trained model expects."""

import joblib
import os

model_path = os.path.join(os.path.dirname(__file__), 'model', 'model.joblib')

if os.path.exists(model_path):
    model = joblib.load(model_path)
    if hasattr(model, 'feature_names_in_'):
        print("Expected features (in order):")
        for i, name in enumerate(model.feature_names_in_):
            print(f"{i+1}. {name}")
        print(f"\nTotal features: {len(model.feature_names_in_)}")
    else:
        print("Model doesn't have feature_names_in_ attribute")
        print("This is a LinearRegression model, checking coef_ length...")
        if hasattr(model, 'coef_'):
            print(f"Model expects {len(model.coef_)} features")
else:
    print(f"Model not found at {model_path}")

