# Machine learning (intentionally not included in v1)

The supplied diet chart contains **no labelled dataset**, so a trained model here would only copy
our own rules and pretending otherwise would be dishonest.

Add ML only when you have:
1. Clearly defined input features and a meaningful target label
2. Enough representative examples, with consent and privacy rights
3. A train/test split
4. Reported accuracy, precision, recall, F1 and a confusion matrix

Possible experiments: Random Forest goal classification, or clustering of user patterns.
Save evaluated models with `joblib.dump(model, "models/goal_model.joblib")`.
Never use a model for medical decisions.
