# Titanic-Disaster

A logistic regression analysis of the [Kaggle Titanic dataset](https://www.kaggle.com/competitions/titanic), predicting which passengers survived. The same analysis is implemented twice, once in Python and once in R. Each runs in its own Docker container. You will need to have docker installed. You may also need to make an account on Kaggle in order to download the datasets.

## Repository layout

```
Titanic-Disaster/
├── README.md
├── .gitignore
└── src/
    ├── data/            # you create this content (see Step 2); ignored by git
    ├── RunCode/         # Python version
    │   ├── Dockerfile
    │   ├── main.py
    │   └── requirements.txt
    └── RScript/         # R version
        ├── Dockerfile
        ├── install_packages.R
        └── main.R
```

The dataset is not included in this repository. You download it yourself in Step 2.

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/), installed and running
- Git
- A free [Kaggle](https://www.kaggle.com) account, to download the data

No local installation of Python or R is needed.

## Step 1: Clone the repository

```bash
git clone https://github.com/alexmiller2363/Titanic-Disaster.git
cd Titanic-Disaster
```

## Step 2: Download the data

1. Sign in to Kaggle and open the [Titanic data page](https://www.kaggle.com/competitions/titanic/data). You may need to click **Join Competition** and accept the rules first.
2. Click **Download All** and unzip the file.
3. Copy **`train.csv`** and **`test.csv`** into the `src/data` folder of this repository (create the folder if it doesn't exist).

Check that both files are there:

```bash
ls src/data
```

You should see `train.csv` and `test.csv`. You don't need `gender_submission.csv`. These files are listed in `.gitignore`, so they will never be committed.

## Step 3: Run the Python version

Run these from the repository root (the `Titanic-Disaster` folder), with Docker Desktop running.

**Build the image** (the first build takes a few minutes):

```bash
docker build -t titanic-python src/RunCode
```

**Run the container**, sharing your data folder with it:

macOS, Linux, or Git Bash on Windows:
```bash
docker run --rm -v "$(pwd)/src/data:/app/data" titanic-python
```

Windows PowerShell:
```powershell
docker run --rm -v "${PWD}\src\data:/app/data" titanic-python
```

If you use Git Bash and get a "file not found" error for the data, put `MSYS_NO_PATHCONV=1` in front of the command:
```bash
MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd)/src/data:/app/data" titanic-python
```

## Step 4: Run the R version

Same idea, from the repository root:

**Build the image** (the first build downloads R and installs `dplyr`, which can take several minutes):

```bash
docker build -t titanic-r src/RScript
```

**Run the container:**

macOS, Linux, or Git Bash on Windows:
```bash
docker run --rm -v "$(pwd)/src/data:/app/data" titanic-r
```

Windows PowerShell:
```powershell
docker run --rm -v "${PWD}\src\data:/app/data" titanic-r
```

The same Git Bash tip from Step 3 applies (`MSYS_NO_PATHCONV=1`).

## What the scripts do

Both scripts follow the same steps and print the result of each one to the terminal:

1. Load `train.csv` and report its size and missing values. `Age` has 177 missing values out of 891 passengers.
2. Clean the data: fill missing `Age` and `Fare` with the median, and encode `Sex` as a number (male = 0, female = 1).
3. Fit a logistic regression using the features `Pclass`, `Sex`, `Age`, `SibSp`, `Parch`, and `Fare`.
4. Report the accuracy on the training set.
5. Load `test.csv`, clean it the same way, and predict survival for each passenger. Print the first 10 predictions and the predicted survival rate by sex and by class.
6. Report accuracy on a held-out set of passengers (see the note below).

The Python version also saves `submission.csv` inside the container in Kaggle's submission format. It is discarded when the container exits and is not needed to check the results.

## Expected output

Your output should match closely. The training accuracy and the test predictions are identical in both languages apart from rounding.

| Result | Python | R |
|---|---|---|
| Training accuracy (891 passengers) | 0.796 | 0.795 |
| Predicted survivors in `test.csv` | 160 of 418 (38.3%) | 160 of 418 (38.3%) |
| Predicted survival, women / men | 0.941 / 0.064 | 0.941 / 0.064 |
| Held-out accuracy | 0.810 | 0.747 |

## Note on test accuracy

Kaggle withholds the true outcomes for `test.csv`, so the file has no `Survived` column and accuracy cannot be computed on it directly. The scripts still predict on `test.csv`. To measure how the model does on unseen passengers, each script fits the model on a random 80% of `train.csv` and scores it on the other 20%. This is the **held-out accuracy** in the table above.

The held-out accuracy differs between Python (0.810) and R (0.747) because the two languages draw different random 20% samples, even with the same seed. The difference reflects which passengers were picked, not a difference between the models. With only about 180 held-out passengers, a gap of this size is normal.

To get a true test score, you can upload a `submission.csv` to Kaggle, which scores it against the hidden labels.

## Troubleshooting

- **`Cannot connect to the Docker daemon`:** Docker Desktop is not running. Start it and wait until it reports that it is running.
- **`FileNotFoundError: data/train.csv` or `cannot open file 'data/train.csv'`:** the data folder was not shared with the container. Check that `train.csv` and `test.csv` are in `src/data`, that you ran the command from the repository root, and that the `-v` option was included. In Git Bash, try the `MSYS_NO_PATHCONV=1` form.
- **`docker run` says it `requires at least 1 argument`:** the image name (`titanic-python` or `titanic-r`) is missing from the end of the command.
- **Edited a script but the output didn't change:** rebuild the image with the `docker build` command. The image contains a copy of the script from the time it was built.
