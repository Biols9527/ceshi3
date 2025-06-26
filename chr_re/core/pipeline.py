from ..core.models import PhyloData, AnalysisResult
from ..methods.base import BaseMethod


class Pipeline:
    """
    Orchestrates the character reconstruction and evolutionary analysis workflow
    by executing a specified analysis method (strategy).
    """

    def __init__(self, method: BaseMethod):
        """
        Initializes the Pipeline with a specific analysis method.

        This uses the Strategy Pattern, where the analysis 'strategy' is injected
        into the pipeline upon creation.

        Args:
            method: An instance of a class that inherits from BaseMethod,
                    e.g., MaximumLikelihoodMethod().
        """
        if not isinstance(method, BaseMethod):
            raise TypeError("The 'method' must be an instance of a BaseMethod subclass.")
        self.method = method
        print(f"Pipeline initialized with method: {type(self.method).__name__}")

    def run(self, data: PhyloData, config: dict | None = None) -> AnalysisResult:
        """
        Runs the analysis using the method provided during initialization.

        Args:
            data: A PhyloData object containing the tree and trait data.
            config: A dictionary containing configuration options for the
                    analysis method.

        Returns:
            An AnalysisResult object from the executed method.
        """
        print(f"Executing method: {type(self.method).__name__}...")
        return self.method.run(data, config)


# Example of how to use the new, flexible pipeline
if __name__ == '__main__':
    from ..core.data_loader import load_phylo_data
    from ..methods.parsimony import ParsimonyMethod

    print("--- Example Pipeline Execution with Fitch Parsimony ---")

    tree_file = "examples/simulated_tree.nwk"
    counts_file = "examples/simulated_counts.csv"

    try:
        # 1. Load data
        print(f"Loading data from {tree_file} and {counts_file}...")
        phylo_data = load_phylo_data(tree_file, counts_file)
        print("Data loaded successfully.")

        # 2. Choose and instantiate the Parsimony method
        parsimony_method = ParsimonyMethod()

        # 3. Create the pipeline, injecting the chosen method
        pipeline = Pipeline(method=parsimony_method)

        # 4. Define the configuration for the analysis
        parsimony_config = {"algorithm": "Fitch"}

        # 5. Run the pipeline
        result = pipeline.run(phylo_data, config=parsimony_config)

        # 6. Print the results
        print("\n--- Analysis Finished ---")
        print(f"Parsimony Score: {result.parameters.get('parsimony_score')}")
        print("\nAnnotated Tree (with ancestral states):")
        # The ete3 tree object's __str__ method provides a nice representation
        print(result.annotated_tree)

    except FileNotFoundError as e:
        print(f"\nError: Could not find data files. {e}")
        print("Please ensure you are running this from the project's root directory")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

