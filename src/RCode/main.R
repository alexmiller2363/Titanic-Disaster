library(dplyr)

features <- c("Pclass", "Sex", "Age", "SibSp", "Parch", "Fare")

train <- read.csv("data/train.csv")
cat("Loaded train.csv:", nrow(train), "rows,", ncol(train), "columns\n")
cat("Missing values in train:\n")
print(colSums(is.na(train[, features])))

# Clean: fill missing values and encode Sex as a number
age_median <- median(train$Age, na.rm = TRUE)
fare_median <- median(train$Fare, na.rm = TRUE)
cat("Filling missing Age with median", age_median, "and Fare with median", fare_median, "\n")

clean <- function(df) {
  df %>%
    mutate(
      Age = ifelse(is.na(Age), age_median, Age),
      Fare = ifelse(is.na(Fare), fare_median, Fare),
      Sex = ifelse(Sex == "female", 1, 0)
    )
}

train <- clean(train)
cat("Using features:", paste(features, collapse = ", "), "\n")

formula <- as.formula(paste("Survived ~", paste(features, collapse = " + ")))

# Fit on the full training set and measure training accuracy
model <- glm(formula, data = train, family = binomial)
train_pred <- as.integer(predict(model, train, type = "response") > 0.5)
cat(sprintf("Training accuracy: %.3f\n", mean(train_pred == train$Survived)))

# test.csv has no Survived labels, so predict on it and report the results
raw_test <- read.csv("data/test.csv")
test <- clean(raw_test)
cat("Loaded test.csv:", nrow(test), "rows,", ncol(test), "columns\n")
test_prob <- predict(model, test, type = "response")
test_pred <- as.integer(test_prob > 0.5)
cat(sprintf("Predicted %d survivors out of %d test passengers (%.1f%%)\n",
            sum(test_pred), length(test_pred), 100 * mean(test_pred)))
cat("Test accuracy cannot be computed on test.csv because it has no Survived column.\n")

# Inspect the test predictions passenger by passenger
results <- data.frame(
  PassengerId = raw_test$PassengerId,
  Name = raw_test$Name,
  Sex = raw_test$Sex,
  Pclass = raw_test$Pclass,
  SurvivalProbability = round(test_prob, 3),
  PredictedSurvived = test_pred
)
cat("First 10 test predictions:\n")
print(head(results, 10), row.names = FALSE)
cat("Predicted survival rate by sex:\n")
print(round(tapply(results$PredictedSurvived, results$Sex, mean), 3))
cat("Predicted survival rate by class:\n")
print(round(tapply(results$PredictedSurvived, results$Pclass, mean), 3))

# Held-out accuracy: fit on 80% of train.csv, score on the other 20%
set.seed(42)
fit_rows <- sample(nrow(train), size = round(0.8 * nrow(train)))
holdout_model <- glm(formula, data = train[fit_rows, ], family = binomial)
val <- train[-fit_rows, ]
val_pred <- as.integer(predict(holdout_model, val, type = "response") > 0.5)
cat(sprintf("Held-out accuracy (%d passengers not used for fitting): %.3f\n",
            nrow(val), mean(val_pred == val$Survived)))
