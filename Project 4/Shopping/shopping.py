import csv
import sys
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():
    """
    Entry point of the program. Handles command-line arguments,
    loads data, trains the model, and evaluates its performance.
    """
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data and split into training and testing sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train the model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file and preprocess it into evidence and labels.
    Returns:
        - evidence: List of feature lists.
        - labels: List of binary labels (1 for True, 0 for False).
    """
    months = {
        "Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3, "May": 4, "June": 5,
        "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11
    }

    evidence, labels = [], []

    with open(filename) as f:
        reader = csv.reader(f)
        headers = next(reader)

        for row in reader:
            evidence.append([
                int(row[0]),                                # Administrative
                float(row[1]),                              # Administrative_Duration
                int(row[2]),                                # Informational
                float(row[3]),                              # Informational_Duration
                int(row[4]),                                # ProductRelated
                float(row[5]),                              # ProductRelated_Duration
                float(row[6]),                              # BounceRates
                float(row[7]),                              # ExitRates
                float(row[8]),                              # PageValues
                float(row[9]),                              # SpecialDay
                months[row[10]],                            # Month
                int(row[11]),                               # OperatingSystems
                int(row[12]),                               # Browser
                int(row[13]),                               # Region
                int(row[14]),                               # TrafficType
                1 if row[15] == "Returning_Visitor" else 0,  # VisitorType
                1 if row[16] == "TRUE" else 0               # Weekend
            ])
            labels.append(1 if row[17] == "TRUE" else 0)    # Revenue

    return evidence, labels


def train_model(evidence, labels):
    """
    Train a k-nearest neighbors model (k=1) using the provided evidence and labels.
    Returns the trained model.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Evaluate the performance of the model's predictions.
    Returns:
        - sensitivity: True positive rate.
        - specificity: True negative rate.
    """
    actual_positive = sum(1 for i in range(len(labels)) if labels[i] == 1 and predictions[i] == 1)
    actual_negative = sum(1 for i in range(len(labels)) if labels[i] == 0 and predictions[i] == 0)
    total_positive = labels.count(1)
    total_negative = labels.count(0)

    sensitivity = actual_positive / total_positive if total_positive else 0
    specificity = actual_negative / total_negative if total_negative else 0

    return sensitivity, specificity


if __name__ == "__main__":
    main()
