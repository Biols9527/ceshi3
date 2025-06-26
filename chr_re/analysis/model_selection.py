"""Functions for model selection, such as comparing AIC scores.
"""

import numpy as np
from ..core.models import AnalysisResult


def calculate_aic(log_likelihood: float, num_params: int) -> float:
    """Calculates the Akaike Information Criterion (AIC)."""
    return 2 * num_params - 2 * log_likelihood


def compare_models(results: list[AnalysisResult]) -> dict:
    """
    Compares different models based on their AnalysisResult objects.

    This function typically uses information criteria like AIC to compare models.
    It requires that the AnalysisResult objects contain a log-likelihood value
    and information about the number of estimated parameters.

    Args:
        results: A list of AnalysisResult objects, where each object is the
                 output of a different model run.

    Returns:
        A dictionary summarizing the comparison, often ranking models by AIC.

    Raises:
        ValueError: If the list of results is empty or if results are missing
                    necessary information (likelihood, number of parameters).
    """
    print("Comparing models...")

    if not results:
        raise ValueError("The list of results to compare cannot be empty.")

    comparison_table = []

    for result in results:
        if result.likelihood is None:
            print(f"Skipping a result because it has no likelihood score (e.g., Parsimony).")
            continue

        # The number of parameters should be stored in the parameters dict.
        # For this example, we'll assume it's under a 'num_params' key.
        if "num_params" not in result.parameters:
            print(
                f"Skipping a result because 'num_params' is not in its parameters dict."
            )
            continue

        log_L = result.likelihood
        k = result.parameters["num_params"]
        aic_score = calculate_aic(log_L, k)

        comparison_table.append(
            {
                "model_name": result.parameters.get("model_name", "Unknown"),
                "log_likelihood": log_L,
                "num_params": k,
                "aic": aic_score,
            }
        )

    if not comparison_table:
        raise ValueError("No valid results found to compare.")

    # Sort the table by AIC score (lower is better)
    comparison_table.sort(key=lambda x: x["aic"])

    return {"comparison": comparison_table}


# Example of how to use this analysis module:
if __name__ == '__main__':
    from ..core.models import AnalysisResult

    print("--- Example Model Comparison ---")

    # 1. Create a list of dummy AnalysisResult objects
    #    Simulating a comparison between a simple (BM) and a complex (OU) model.
    results_list = [
        AnalysisResult(
            annotated_tree=None,
            parameters={"model_name": "BM", "num_params": 1, "sigma_sq": 0.1},
            likelihood=-55.4, # Lower likelihood
        ),
        AnalysisResult(
            annotated_tree=None,
            parameters={"model_name": "OU", "num_params": 3, "alpha": 0.2, "sigma_sq": 0.08},
            likelihood=-50.1, # Higher likelihood, but more params
        ),
        AnalysisResult(
            annotated_tree=None,
            parameters={"parsimony_score": 10}, # No likelihood, should be skipped
            likelihood=None,
        ),
    ]

    print(f"Comparing {len(results_list)} model results...")
    try:
        comparison = compare_models(results_list)
        import json
        print("--> Comparison Result:")
        print(json.dumps(comparison, indent=2))
    except ValueError as e:
        print(f"Caught expected error: {e}")

    print("\nModel selection structure implemented.")
"""