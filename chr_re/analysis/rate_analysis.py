"""Functions for analyzing evolutionary rates from the results of a phylogenetic analysis.
"""

from ..core.models import AnalysisResult


def calculate_evolutionary_rates(result: AnalysisResult, config: dict | None = None) -> dict:
    """
    Calculates evolutionary rates based on the parameters estimated by an analysis method.

    This function acts as a dispatcher, calling the appropriate rate calculation
    logic based on the contents of the AnalysisResult object.

    Args:
        result: The AnalysisResult object from a completed analysis run.
        config: A dictionary for any additional configuration.

    Returns:
        A dictionary containing the calculated rates. The exact contents will
        depend on the analysis method that produced the result.

    Raises:
        ValueError: If the required parameters for rate calculation are not
                    found in the result object.
    """
    print("Analyzing evolutionary rates...")

    # Example: Check for a 'sigma_sq' parameter, typical of BM models in ML.
    if "sigma_sq" in result.parameters:
        # In a real implementation, you would perform calculations here.
        # For now, we just acknowledge we found the parameter.
        rate = result.parameters["sigma_sq"]
        print(f"Found 'sigma_sq' parameter for rate analysis: {rate}")
        return {"method": "Maximum Likelihood (BM)", "rate_sigma_sq": rate}

    # Example: Check for a 'rate' parameter from a Bayesian posterior.
    if "rate_posterior" in result.parameters:
        # Here you might calculate the mean, median, and HPD of the posterior.
        # For now, we just acknowledge it.
        posterior_summary = result.parameters["rate_posterior"]
        print(f"Found 'rate_posterior' for rate analysis: {posterior_summary}")
        return {"method": "Bayesian", "rate_summary": posterior_summary}

    # Add more checks for other models and methods (e.g., OU models have alpha, sigma, theta)

    raise ValueError(
        "Could not determine how to calculate rates from the provided AnalysisResult. "
        "No recognized rate parameters found."
    )

# Example of how to use this analysis module:
if __name__ == '__main__':
    from ..core.models import AnalysisResult

    print("--- Example Rate Analysis ---")

    # 1. Create a dummy AnalysisResult, simulating one from a Maximum Likelihood run
    ml_result = AnalysisResult(
        annotated_tree=None,  # Dummy data
        parameters={"sigma_sq": 0.05, "aic": 102.3}, # ML result might have sigma_sq
        likelihood= -51.15
    )

    print("\nAnalyzing a simulated ML result:")
    try:
        ml_rates = calculate_evolutionary_rates(ml_result)
        print(f"--> Calculated rates: {ml_rates}")
    except ValueError as e:
        print(f"Caught expected error: {e}")


    # 2. Create another dummy result, simulating one from a Bayesian run
    bayesian_result = AnalysisResult(
        annotated_tree=None, # Dummy data
        parameters={"rate_posterior": {'mean': 0.06, 'hpd_95': [0.02, 0.10]}},
        raw_output=None # Dummy data
    )

    print("\nAnalyzing a simulated Bayesian result:")
    try:
        bayesian_rates = calculate_evolutionary_rates(bayesian_result)
        print(f"--> Calculated rates: {bayesian_rates}")
    except ValueError as e:
        print(f"Caught expected error: {e}")


    # 3. Create a result that will fail, simulating one from Parsimony
    parsimony_result = AnalysisResult(
        annotated_tree=None, # Dummy data
        parameters={"parsimony_score": 15}, # Parsimony doesn't estimate rate
        likelihood=None
    )

    print("\nAnalyzing a simulated Parsimony result (expected to fail):")
    try:
        parsimony_rates = calculate_evolutionary_rates(parsimony_result)
        print(f"--> Calculated rates: {parsimony_rates}")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    print("\nRate analysis structure implemented.")
"""