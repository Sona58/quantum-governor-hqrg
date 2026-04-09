import numpy as np

def normalize_features(features: list) -> np.ndarray:
    """
    Min-Max Scaling to fit data into the [0, pi] range 
    required for the ZZFeatureMap.
    """
    # Assuming features are: [loan_amount, credit_score, income, debt]
    # In a real app, you'd use a saved StandardScaler or MinMaxScaler object
    raw_array = np.array(features)
    
    # Simple normalization logic for demonstration
    # Ensures all values are between 0 and pi
    normalized = (raw_array - np.min(raw_array)) / (np.max(raw_array) - np.min(raw_array) + 1e-9)
    return normalized * np.pi