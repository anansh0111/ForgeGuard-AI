# ml/

Place your trained model file here:

```
ml/
└── best_model.pkl   ← your LightGBM model (pickle)
```

This directory is mounted read-only into the backend container at `/app/ml/`.

## Expected model interface

The model must support scikit-learn's `predict_proba` API:

```python
model.predict_proba(X)  # X shape: (n, 6)
# Returns: array of shape (n, 2) — [prob_no_failure, prob_failure]
```

## Feature order (must match training)

1. Air_temperature__K_
2. Process_temperature__K_
3. Rotational_speed__rpm_
4. Torque__Nm_
5. Tool_wear__min_
6. temp_difference

## Quick test

```python
import pickle, numpy as np
with open("ml/best_model.pkl", "rb") as f:
    model = pickle.load(f)

X = np.array([[300.0, 310.0, 1500.0, 40.0, 100.0, 10.0]])
print(model.predict_proba(X))  # Should print [[p0, p1]]
```
