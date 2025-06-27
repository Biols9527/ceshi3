from .config import DefaultConfig
from .data_loader import DataLoader
from .pipeline import Pipeline
from ..methods.parsimony import ParsimonyMethod
from ..methods.maximum_likelihood import MaximumLikelihoodMethod
from ..methods.bayesian import BayesianMethod
from ..methods.ensemble import EnsembleMethod
# Potential future imports for visualization
# from ..visualization.interactive import InteractiveVisualizer

class ChromosomeReconstructionFramework:
    """
    Main entry point and orchestrator for the chromosome reconstruction and analysis.
    This class integrates data loading, reconstruction, event detection, and visualization.
    """
    def __init__(self, config=None):
        """
        Initializes the ChromosomeReconstructionFramework.

        Args:
            config: A configuration object. If None, DefaultConfig is used.
        """
        self.config = config or DefaultConfig()
        self.data_loader = DataLoader(self.config) # DataLoader can take config for future use
        self.pipeline = None # Pipeline will be instantiated with a specific method later
        
        self.phylo_data = None # Will hold PhyloData object from DataLoader
        self.tree = None # Convenience attribute, points to phylo_data.tree
        self.counts = None # Convenience attribute, points to phylo_data.traits
        self.reconstruction_results = None
        self.events = None
        
        print(f"ChromosomeReconstructionFramework initialized with config: {type(self.config).__name__}")

    def _get_method_instance(self, method_name: str):
        """
        Factory helper method to get an instance of a reconstruction method class.
        """
        if method_name.lower() == 'parsimony':
            return ParsimonyMethod()
        elif method_name.lower() == 'ml' or method_name.lower() == 'maximum_likelihood':
            return MaximumLikelihoodMethod()
        elif method_name.lower() == 'bayesian':
            return BayesianMethod()
        elif method_name.lower() == 'ensemble':
            return EnsembleMethod()
        else:
            raise ValueError(f"Unknown reconstruction method: {method_name}")

    def load_data(self, tree_file: str, counts_file: str, tree_format: str = 'newick', **kwargs):
        """
        Loads and validates tree and chromosome count data using the DataLoader.

        Args:
            tree_file (str): Path to the phylogenetic tree file.
            counts_file (str): Path to the chromosome counts data file.
            tree_format (str): Format of the tree file (e.g., 'newick', 'nexus'). Defaults to 'newick'.
            **kwargs: Additional keyword arguments for loading chromosome counts (e.g., pandas.read_csv options).

        Raises:
            NotImplementedError: As the full implementation of data_loader methods is pending.
        """
        print(f"Framework: Loading tree from {tree_file} and counts from {counts_file} using {type(self.data_loader).__name__}")
        try:
            # DataLoader's load_phylo_data now returns a PhyloData object and handles validation.
            # Pass tree_format and any other relevant kwargs (like species_col, counts_col if they differ from defaults)
            # The **kwargs in framework.load_data are intended for pandas read_csv options.
            phylo_data_object = self.data_loader.load_phylo_data(
                tree_file,
                counts_file,
                tree_format=tree_format,
                **kwargs # these are kwargs for pd.read_csv
            )
            self.phylo_data = phylo_data_object # Store the whole object
            self.tree = self.phylo_data.tree
            self.counts = self.phylo_data.traits # This is a DataFrame
            print("Framework: Data loaded and validated successfully.")
        except FileNotFoundError as e:
            print(f"Framework: Error - {e}")
            # Re-raise or handle as appropriate for the framework's error handling strategy
            raise
        except ValueError as e:
            print(f"Framework: Error - {e}")
            # Re-raise or handle
            raise
        except Exception as e:
            print(f"Framework: An unexpected error occurred during data loading: {e}")
            # Re-raise or handle
            raise

    def reconstruct_ancestors(self, method: str = 'ensemble', **kwargs):
        """
        Performs ancestral state reconstruction using the configured pipeline and method.

        Args:
            method (str, optional): The reconstruction method to use (e.g., 'parsimony', 'ml', 'bayesian', 'ensemble').
                                    Defaults to 'ensemble' (though actual default method might come from config).
                                    This 'method' string needs to be mapped to an actual method instance for the Pipeline.
            **kwargs: Additional keyword arguments for the reconstruction method/pipeline configuration.

        Raises:
            NotImplementedError: If the pipeline integration or method selection is not fully implemented.
            ValueError: If data has not been loaded first.
        """
        if self.phylo_data is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

        print(f"Framework: Reconstructing ancestors using '{method}' method...") # Added quotes for clarity

        try:
            method_instance = self._get_method_instance(method_name=method)

            # Instantiate the pipeline with the chosen method
            # Note: self.pipeline is currently None or could hold a default.
            # For each run, we might want a fresh pipeline if its state is important,
            # or ensure self.pipeline can have its method updated.
            # The current Pipeline design takes method in __init__.
            current_pipeline = Pipeline(method=method_instance)

            # The 'kwargs' passed to reconstruct_ancestors are method-specific configurations
            # For example, for parsimony, it might be {'algorithm': 'Fitch'}
            # For ML, it might be {'model': 'BM'}
            self.reconstruction_results = current_pipeline.run(data=self.phylo_data, config=kwargs)

            print(f"Framework: Ancestor reconstruction using '{method}' complete.")
            if self.reconstruction_results:
                # Attempt to access a common parameter like 'model_name' or 'parsimony_score' if available
                result_params = self.reconstruction_results.parameters
                param_info = ""
                if result_params:
                    if 'model_name' in result_params:
                        param_info = f"Model: {result_params['model_name']}"
                    if 'parsimony_score' in result_params:
                        param_info += f" Score: {result_params['parsimony_score']}"
                print(f"Framework: Results obtained. {param_info.strip()}")

        except NotImplementedError as e:
            # This will catch NotImplementedError raised by the specific method (e.g., ML, Bayesian)
            print(f"Framework: The method '{method}' is not fully implemented: {e}")
            # Re-raise so it's clear in testing that the specific method isn't ready
            raise
        except Exception as e:
            print(f"Framework: Error during ancestor reconstruction with method '{method}': {e}")
            # Re-raise for general errors
            raise
            
    def detect_events(self, **kwargs):
        """
        Detects evolutionary events based on reconstruction results using the pipeline or a dedicated module.

        Args:
            **kwargs: Additional keyword arguments for the event detection method.

        Raises:
            NotImplementedError: As the full implementation of event detection is pending.
        """
        # Placeholder: Will use self.pipeline or a dedicated event detection module
        print("Framework: Detecting events...")
        # self.events = self.pipeline.run_event_detection(self.reconstruction_results, **kwargs)
        # print("Framework: Event detection complete.")
        raise NotImplementedError("Event detection not fully implemented yet.")
            
    def visualize(self, **kwargs):
        """
        # if self.reconstruction_results is None:
        #     print("Framework: Ancestral states not reconstructed. Please reconstruct ancestors first.")
        #     return None
        #
        # try:
        #     # Assume pipeline has a method for event detection, or a separate module is used.
        #     # self.events = self.pipeline.run_event_detection(self.reconstruction_results, **kwargs)
        #     # Or:
        Visualizes the phylogenetic tree, reconstructed states, and detected events.

        Args:
            **kwargs: Additional keyword arguments for visualization methods.

        Raises:
            NotImplementedError: As the full implementation of visualization is pending.
        """
        # Placeholder: Will use a visualization module
        print("Framework: Visualizing results...")
        # visualizer = InteractiveVisualizer(self.config) # Or some other visualizer
        # visualizer.plot_tree_with_states(self.tree, self.reconstruction_results, **kwargs)
        # if self.events:
        #     visualizer.plot_event_timeline(self.events, **kwargs)
        raise NotImplementedError("Visualization not fully implemented yet.")
        # if self.tree is None:
        #     print("Framework: No tree data to visualize.")
        #     return
        #
        # try:
        #     # visualizer = InteractiveVisualizer(self.config) # Or another visualizer type
        #     # if self.reconstruction_results:
        #     #     visualizer.plot_tree_with_states(self.tree, self.reconstruction_results, **kwargs)
        #     # else:
        #     #     visualizer.plot_tree(self.tree, **kwargs) # Basic tree plot
        #
        #     # if self.events:
        #     #     visualizer.plot_event_timeline(self.events, **kwargs) # Or plot events on tree
        #     print("Framework: Visualization initiated (actual visualization depends on implementation).")
        # except Exception as e:
        #     print(f"Framework: Error during visualization: {e}")
        #     raise
        raise NotImplementedError("Visualization not fully implemented yet.")

if __name__ == '__main__':
    print("--- Initializing ChromosomeReconstructionFramework with default config ---")
    framework = ChromosomeReconstructionFramework()
    
    # Example of how methods would be called (will raise NotImplementedError)
    dummy_tree_file = "dummy_framework_tree.nwk"
    dummy_counts_file = "dummy_framework_counts.csv"
    
    # Create dummy files with default column names for DataLoader
    # DataLoader expects 'species' and 'count' by default.
    with open(dummy_tree_file, "w") as f:
        f.write("((taxonA:1,taxonB:1):1,taxonC:2);") # Using taxonA, B, C to match counts
    with open(dummy_counts_file, "w") as f:
        f.write("species,count\ntaxonA,10\ntaxonB,12\ntaxonC,14")

    print("\n--- Testing load_data ---")
    try:
        # Test with default column names ('species', 'count')
        framework.load_data(dummy_tree_file, dummy_counts_file)
        if framework.phylo_data:
            print(f"SUCCESS: Data loaded. Tree tips: {framework.tree.get_leaf_names()}, Counts head:\n{framework.counts.head()}")
        else:
            print("FAILURE: Data not loaded, phylo_data is None.")
    except Exception as e: # Catch any exception during load_data
        print(f"ERROR during load_data: {e}")

    print("\n--- Testing reconstruct_ancestors (Parsimony Fitch) ---")
    if framework.phylo_data: # Only proceed if data was loaded
        try:
            # ParsimonyMethod with Fitch is implemented.
            # The 'algorithm' Fitch is a kwarg for the ParsimonyMethod's run config.
            framework.reconstruct_ancestors(method='parsimony', algorithm='Fitch')
            if framework.reconstruction_results:
                print(f"SUCCESS: Parsimony reconstruction complete. Score: {framework.reconstruction_results.parameters.get('parsimony_score')}")
                # print(f"Annotated tree: {framework.reconstruction_results.annotated_tree.get_ascii(attributes=['name', 'state', 'states'])}")
            else:
                print("FAILURE: Reconstruction finished but no results stored.")
        except NotImplementedError as e:
            print(f"ERROR: reconstruct_ancestors call failed as method is not fully implemented: {e}")
        except Exception as e:
            print(f"ERROR during reconstruct_ancestors (Parsimony): {e}")
    else:
        print("SKIPPED: reconstruct_ancestors test because data loading failed or was skipped.")

    print("\n--- Testing reconstruct_ancestors (ML - expected to be not implemented) ---")
    if framework.phylo_data: # Only proceed if data was loaded
        try:
            # MaximumLikelihoodMethod is expected to raise NotImplementedError.
            # It needs a 'model' in its config.
            framework.reconstruct_ancestors(method='ml', model='BM')
            print("UNEXPECTED SUCCESS: ML reconstruction ran without error (should be NotImplemented).")
        except NotImplementedError as e:
            print(f"SUCCESS: Caught expected NotImplementedError for ML method: {e}")
        except Exception as e:
            print(f"ERROR during reconstruct_ancestors (ML): {e}")
    else:
        print("SKIPPED: reconstruct_ancestors ML test because data loading failed or was skipped.")

    # Reset for next potential tests if any were added
    framework.phylo_data = None
    framework.tree = None
    framework.counts = None
    framework.reconstruction_results = None

    print("\n--- Testing detect_events ---")
    try:
        # Simulate reconstruction results being available
        framework.reconstruction_results = "dummy_reconstruction_results"
        framework.detect_events()
    except NotImplementedError as e:
        print(f"Caught expected error: {e}")
    finally:
        framework.reconstruction_results = None # Reset

    print("\n--- Testing visualize ---")
    try:
        # Simulate tree being available
        framework.tree = "dummy_tree_object"
        framework.visualize()
    except NotImplementedError as e:
        print(f"Caught expected error: {e}")
    finally:
        framework.tree = None # Reset

    # Clean up dummy files
    import os
    os.remove(dummy_tree_file)
    os.remove(dummy_counts_file)
    
    print("\nChromosomeReconstructionFramework structure implemented.")
