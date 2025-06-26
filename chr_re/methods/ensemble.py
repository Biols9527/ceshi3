"""from ..core.models import PhyloData, AnalysisResult
from .base import BaseMethod


class EnsembleMethod(BaseMethod):
    """
    Implements an ensemble approach by running multiple analysis methods and
    combining their results.
    """

    def run(self, data: PhyloData, config: dict | None = None) -> AnalysisResult:
        """
        Executes the ensemble analysis.

        This method iterates through a list of other methods, runs them, and
        aggregates their results.

        Args:
            data: A PhyloData object containing the tree and trait data.
            config: A dictionary containing the configuration. It must include a
                    'methods' key, which is a list of tuples. Each tuple
                    contains a BaseMethod instance and its specific config.
                    Example:
                    {
                        'methods': [
                            (MaximumLikelihoodMethod(), {'model': 'BM'}),
                            (ParsimonyMethod(), {'algorithm': 'Fitch'})
                        ]
                    }

        Returns:
            An AnalysisResult object. The 'raw_output' will contain a list of
            individual results from each method in the ensemble.

        Raises:
            ValueError: If the config is missing the 'methods' list or if the
                        list is improperly formatted.
        """
        if config is None or "methods" not in config:
            raise ValueError(
                "EnsembleMethod requires a 'methods' list in its config."
            )

        method_configs = config["methods"]
        if not isinstance(method_configs, list):
            raise ValueError("The 'methods' config must be a list.")

        print(f"Running Ensemble analysis with {len(method_configs)} methods...")

        all_results = []
        for i, method_config_tuple in enumerate(method_configs):
            if not (isinstance(method_config_tuple, tuple) and len(method_config_tuple) == 2):
                raise ValueError(f"Item {i} in 'methods' list is not a (method, config) tuple.")

            method, method_config = method_config_tuple
            if not isinstance(method, BaseMethod):
                raise TypeError(f"Item {i} in 'methods' list is not a valid BaseMethod instance.")

            print(f"---> Running method {i+1}/{len(method_configs)}: {type(method).__name__}")
            try:
                result = method.run(data, method_config)
                all_results.append(result)
            except Exception as e:
                print(f"    Method {type(method).__name__} failed: {e}")
                # Depending on desired behavior, you could stop or continue
                # For now, we'll just print the error and continue
                all_results.append({"error": str(e), "method": type(method).__name__})


        # The combination logic here is simple: just return all results.
        # A more sophisticated implementation could average parameters,
        # vote on ancestral states, etc.
        return AnalysisResult(
            annotated_tree=None,  # No single tree represents the ensemble yet
            parameters={"ensemble_size": len(all_results)},
            likelihood=None,
            raw_output=all_results
        )
"""