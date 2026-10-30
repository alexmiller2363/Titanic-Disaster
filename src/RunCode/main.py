import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

FEATURES = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare"]

train = pd.read_csv("data/train.csv")
print(f"Loaded train.csv: {train.shape[0]} rows, {train.shape[1]} columns")
print("Missing values in train:")
print(train[FEATURES].isnull().sum())

# Clean: fill missing values and encode Sex as a number
age_median = train["Age"].median()
fare_median = train["Fare"].median()
print(f"Filling missing Age with median {age_median} and Fare with median {fare_median}")


def clean(df):
    df = df.copy()
    df["Age"] = df["Age"].fillna(age_median)
    df["Fare"] = df["Fare"].fillna(fare_median)
    df["Sex"] = df["Sex"].map({"male": 0, "female": 1})
    return df


train = clean(train)
print(f"Using features: {FEATURES}")

# Fit on the full training set and measure training accuracy
X = train[FEATURES]
y = train["Survived"]
model = LogisticRegression(max_iter=1000)
model.fit(X, y)
train_acc = accuracy_score(y, model.predict(X))
print(f"Training accuracy: {train_acc:.3f}")

# test.csv has no Survived labels, so predict on it and report the results
test = clean(pd.read_csv("data/test.csv"))
print(f"Loaded test.csv: {test.shape[0]} rows, {test.shape[1]} columns")
test_preds = model.predict(test[FEATURES])
print(f"Predicted {test_preds.sum()} survivors out of {len(test_preds)} test passengers "
      f"({test_preds.mean():.1%})")
print("Test accuracy cannot be computed on test.csv because it has no Survived column.")

# Inspect the test predictions passenger by passenger
raw_test = pd.read_csv("data/test.csv")
results = pd.DataFrame({
    "PassengerId": raw_test["PassengerId"],
    "Name": raw_test["Name"],
    "Sex": raw_test["Sex"],
    "Pclass": raw_test["Pclass"],
    "SurvivalProbability": model.predict_proba(test[FEATURES])[:, 1].round(3),
    "PredictedSurvived": test_preds,
})
print("First 10 test predictions:")
print(results.head(10).to_string(index=False))
print("Predicted survival rate by sex:")
print(results.groupby("Sex")["PredictedSurvived"].mean().round(3))
print("Predicted survival rate by class:")
print(results.groupby("Pclass")["PredictedSurvived"].mean().round(3))

# Save in Kaggle's submission format to get a true test score by uploading it
results[["PassengerId", "PredictedSurvived"]].rename(
    columns={"PredictedSurvived": "Survived"}
).to_csv("submission.csv", index=False)
print("Saved submission.csv (upload to Kaggle to score on the hidden test labels)")

# Held-out accuracy: fit on 80% of train.csv, score on the other 20%
X_fit, X_val, y_fit, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
holdout_model = LogisticRegression(max_iter=1000).fit(X_fit, y_fit)
holdout_acc = accuracy_score(y_val, holdout_model.predict(X_val))
print(f"Held-out accuracy ({len(y_val)} passengers not used for fitting): {holdout_acc:.3f}")
