from ..core.models import PhyloData, AnalysisResult # Corrected import
from .base import BaseMethod
# Need to import other methods if they are to be used directly in examples,
# but EnsembleMethod itself takes instances, so direct import not strictly needed here for its own code.
# from .maximum_likelihood import MaximumLikelihoodMethod # Example
# from .parsimony import ParsimonyMethod # Example

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
                    should contain a BaseMethod *instance* and its specific config dict.
                    Example:
                    {
                        'methods': [
                            (ParsimonyMethod(), {'algorithm': 'Fitch'}),
                            # (MaximumLikelihoodMethod(), {'model': 'BM'}), # If ML was ready
                        ]
                    }

        Returns:
            An AnalysisResult object. The 'raw_output' will contain a list of
            individual results from each method in the ensemble. The 'parameters'
            field will include the number of methods run.

        Raises:
            ValueError: If the config is missing the 'methods' list or if the
                        list is improperly formatted (e.g., not a list of (BaseMethod instance, dict) tuples).
            TypeError: If an item in the 'methods' list is not a BaseMethod instance.
        """
        if config is None or "methods" not in config:
            raise ValueError(
                "EnsembleMethod requires a 'methods' list in its config. "
                "This list should contain (method_instance, method_config_dict) tuples."
            )

        method_configs_list = config["methods"]
        if not isinstance(method_configs_list, list):
            raise ValueError("The 'methods' config value must be a list.")

        if not method_configs_list:
            print("Warning: Ensemble 'methods' list is empty. No analysis will be performed.")
            return AnalysisResult(
                annotated_tree=None,
                parameters={"ensemble_size": 0, "info": "No methods provided"},
                likelihood=None,
                raw_output=[]
            )

        print(f"Running Ensemble analysis with {len(method_configs_list)} configured method(s)...")

        all_individual_results = []
        for i, method_tuple in enumerate(method_configs_list):
            if not (isinstance(method_tuple, tuple) and len(method_tuple) == 2):
                raise ValueError(
                    f"Item {i} in 'methods' list is not a (BaseMethod_instance, config_dict) tuple. "
                    f"Got: {type(method_tuple)}"
                )

            method_instance, specific_method_config = method_tuple

            if not isinstance(method_instance, BaseMethod):
                raise TypeError(
                    f"Item {i} in 'methods' list does not have a valid BaseMethod instance as its first element. "
                    f"Got: {type(method_instance)}"
                )
            if not isinstance(specific_method_config, dict):
                 raise ValueError(
                    f"Item {i} for method {type(method_instance).__name__} in 'methods' list does not have a "
                    f"dictionary as its second element (config). Got: {type(specific_method_config)}"
                )


            print(f"---> Running method {i+1}/{len(method_configs_list)}: {type(method_instance).__name__} "
                  f"with config: {specific_method_config}")
            try:
                result = method_instance.run(data, specific_method_config)
                all_individual_results.append(result)
            except NotImplementedError as e:
                print(f"    Method {type(method_instance).__name__} is not fully implemented: {e}")
                all_individual_results.append({
                    "status": "not_implemented",
                    "method": type(method_instance).__name__,
                    "error": str(e)
                })
            except Exception as e:
                print(f"    Method {type(method_instance).__name__} failed with error: {e}")
                # Depending on desired behavior, one could stop or continue.
                # For now, log error and continue.
                all_individual_results.append({
                    "status": "error",
                    "method": type(method_instance).__name__,
                    "error": str(e)
                })

        # The combination logic here is simple: just return all results.
        # A more sophisticated implementation could average parameters, vote on ancestral states, etc.
        # The annotated_tree is set to None as there's no single tree for the ensemble in this basic setup.
        return AnalysisResult(
            annotated_tree=None,
            parameters={"ensemble_size": len(all_individual_results), "methods_configured": len(method_configs_list)},
            likelihood=None, # Likelihood combination would be model-specific and complex
            raw_output=all_individual_results
        )