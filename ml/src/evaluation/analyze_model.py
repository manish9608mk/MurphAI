"""
Model analysis utilities for MurphAI.

This module analyzes the trained baseline worker-job
matching model and explains which features contribute
most strongly to the model's predictions.
"""

from pathlib import Path

import pandas as pd

from ml.src.data.data_loader import load_and_validate_dataset
from ml.src.data.dataset_split import split_dataset
from ml.src.features.feature_engineering import prepare_features
from ml.src.models.model_io import load_model


# ============================================================
# Configuration
# ============================================================

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "worker_job_baseline.joblib"
)


# ============================================================
# Load Model and Features
# ============================================================


def load_analysis_data():
    """
    Load the dataset, prepare features, split the dataset,
    and load the trained baseline model.

    Returns
    -------
    tuple
        Trained model and test feature matrix.
    """

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = load_and_validate_dataset()

    # --------------------------------------------------------
    # Prepare features
    # --------------------------------------------------------

    X, y = prepare_features(df)

    # --------------------------------------------------------
    # Split dataset
    # --------------------------------------------------------

    (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    ) = split_dataset(X, y)

    # --------------------------------------------------------
    # Load trained model
    # --------------------------------------------------------

    model = load_model(MODEL_PATH)

    return model, X_test


# ============================================================
# Extract Feature Importance
# ============================================================


def extract_feature_importance(
    model,
    feature_names: list[str],
) -> pd.DataFrame:
    """
    Extract feature importance from the trained model.

    Supports:

        - Tree-based models using feature_importances_
        - Linear models using coef_

    Parameters
    ----------
    model : object
        Trained scikit-learn model.

    feature_names : list[str]
        Names of the model features.

    Returns
    -------
    pd.DataFrame
        Feature importance table.
    """

    # --------------------------------------------------------
    # Determine the actual estimator
    # --------------------------------------------------------

    estimator = model

    if hasattr(model, "steps"):
        estimator = model.steps[-1][1]

    # --------------------------------------------------------
    # Tree-based model
    # --------------------------------------------------------

    if hasattr(estimator, "feature_importances_"):

        importance_values = estimator.feature_importances_

    # --------------------------------------------------------
    # Linear model
    # --------------------------------------------------------

    elif hasattr(estimator, "coef_"):

        coefficients = estimator.coef_

        if coefficients.ndim == 1:
            importance_values = abs(coefficients)

        else:
            importance_values = abs(coefficients[0])

    else:

        raise ValueError(
            "The provided model does not expose "
            "feature_importances_ or coef_. "
            f"Model type: {type(estimator).__name__}"
        )

    # --------------------------------------------------------
    # Validate feature count
    # --------------------------------------------------------

    if len(feature_names) != len(importance_values):

        raise ValueError(
            "Number of feature names does not match "
            "number of importance values."
        )

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importance_values,
        }
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    importance = importance.sort_values(
        by="importance",
        ascending=False,
        ignore_index=True,
    )

    return importance


# ============================================================
# Analyze Feature Direction
# ============================================================


def analyze_feature_direction(
    model,
    feature_names: list[str],
) -> pd.DataFrame:
    """
    Analyze the direction of influence for linear models.

    Positive coefficients indicate that larger feature
    values push predictions toward successful outcomes.

    Negative coefficients indicate that larger feature
    values push predictions toward unsuccessful outcomes.

    Parameters
    ----------
    model : object
        Trained model.

    feature_names : list[str]
        Feature names.

    Returns
    -------
    pd.DataFrame
        Feature coefficients and direction.
    """

    # --------------------------------------------------------
    # Determine estimator
    # --------------------------------------------------------

    estimator = model

    if hasattr(model, "steps"):
        estimator = model.steps[-1][1]

    # --------------------------------------------------------
    # Linear models only
    # --------------------------------------------------------

    if not hasattr(estimator, "coef_"):

        raise ValueError(
            "Feature direction analysis requires a "
            "linear model exposing coef_."
        )

    coefficients = estimator.coef_

    if coefficients.ndim == 1:
        coefficients = coefficients
    else:
        coefficients = coefficients[0]

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    analysis = pd.DataFrame(
        {
            "feature": feature_names,
            "coefficient": coefficients,
        }
    )

    # --------------------------------------------------------
    # Determine direction
    # --------------------------------------------------------

    analysis["direction"] = analysis["coefficient"].apply(
        lambda value: (
            "positive"
            if value > 0
            else "negative"
            if value < 0
            else "neutral"
        )
    )

    # --------------------------------------------------------
    # Sort by absolute influence
    # --------------------------------------------------------

    analysis["absolute_coefficient"] = (
        analysis["coefficient"].abs()
    )

    analysis = analysis.sort_values(
        by="absolute_coefficient",
        ascending=False,
        ignore_index=True,
    )

    return analysis


# ============================================================
# Main Analysis
# ============================================================


def main() -> None:
    """
    Run MurphAI baseline model analysis.
    """

    # --------------------------------------------------------
    # Load model and data
    # --------------------------------------------------------

    model, X_test = load_analysis_data()

    feature_names = list(X_test.columns)

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    importance = extract_feature_importance(
        model=model,
        feature_names=feature_names,
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    print()
    print("MurphAI Baseline Model Analysis")
    print("=" * 45)

    # --------------------------------------------------------
    # Model information
    # --------------------------------------------------------

    print()
    print("Model")
    print("-" * 45)

    estimator = model

    if hasattr(model, "steps"):
        estimator = model.steps[-1][1]

    print(
        f"Model type: {type(estimator).__name__}"
    )

    print(
        f"Test samples: {len(X_test)}"
    )

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    print()
    print("Feature Importance")
    print("-" * 45)

    print(
        importance.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Linear model analysis
    # --------------------------------------------------------

    if hasattr(estimator, "coef_"):

        direction = analyze_feature_direction(
            model=model,
            feature_names=feature_names,
        )

        print()
        print("Feature Direction")
        print("-" * 45)

        print(
            direction.to_string(
                index=False
            )
        )

    # --------------------------------------------------------
    # Top features
    # --------------------------------------------------------

    print()
    print("Top 5 Features")
    print("-" * 45)

    top_features = importance.head(5)

    for index, row in top_features.iterrows():

        print(
            f"{index + 1}. "
            f"{row['feature']} "
            f"({row['importance']:.6f})"
        )


# ============================================================
# Entry Point
# ============================================================


if __name__ == "__main__":
    main()