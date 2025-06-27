import pandas as pd
from ete3 import Tree

# Assuming DefaultConfig might be used or passed, though not strictly necessary for current load_phylo_data
# from .config import DefaultConfig
from .models import PhyloData

class DataLoader:
    """
    Handles loading and validation of phylogenetic trees and associated trait data.
    """
    def __init__(self, config=None):
        """
        Initializes the DataLoader.

        Args:
            config: A configuration object. Currently not used by load_phylo_data
                    but can be used for future enhancements (e.g., default file paths, column names).
        """
        self.config = config
        # print(f"DataLoader initialized with config: {type(self.config).__name__ if self.config else 'None'}")
        # Internal storage for loaded data, if we want DataLoader to hold state
        # self.tree = None
        # self.traits = None
        # self.phylo_data_object = None

    def load_phylo_data(
        self,
        tree_path: str,
        counts_path: str,
        tree_format: int | str = 0, # Default ETE tree format for Newick, can accept str
        species_col: str = "species", # Default column name for species in counts file
        counts_col: str = "count",    # Default column name for counts in counts file
        **kwargs # To catch any other pandas read_csv options passed from framework
    ) -> PhyloData:
        """
        Loads a phylogenetic tree and corresponding trait data into a unified
        PhyloData object. Also validates the consistency between tree tips and trait data.

        Args:
            tree_path (str): Path to the phylogenetic tree file (e.g., in Newick format).
            counts_path (str): Path to the CSV file containing trait data.
            tree_format (int | str): The format code (int) or name (str) for the tree file, as used by ete3.
                                     Defaults to 0 (Newick). Supported strings: 'newick', 'nexus'.
            species_col (str): The name of the column in the CSV that contains species names.
                               Defaults to "species".
            counts_col (str): The name of the column in the CSV that contains the trait counts.
                              Defaults to "count".
            **kwargs: Additional keyword arguments for pd.read_csv (e.g. sep, header).


        Returns:
            PhyloData: A PhyloData object containing the loaded tree and trait data.

        Raises:
            FileNotFoundError: If either the tree or counts file cannot be found.
            ValueError: If the species names in the tree and counts file do not match,
                        or if the specified columns are not in the CSV file, or invalid tree_format string.
        """

        actual_tree_format: int
        if isinstance(tree_format, str):
            format_lower = tree_format.lower()
            if format_lower == 'newick':
                actual_tree_format = 0
            elif format_lower == 'nexus':
                actual_tree_format = 1 # Common ETE3 code for Nexus, verify if different
            # Add other common formats like 'phyloxml' (often 6), 'nexml' (often 5) if needed
            else:
                raise ValueError(f"Unsupported tree_format string: '{tree_format}'. Use 'newick', 'nexus', or an integer code.")
        elif isinstance(tree_format, int):
            actual_tree_format = tree_format
        else:
            raise TypeError(f"tree_format must be an integer or string, not {type(tree_format)}")

        # Load the phylogenetic tree
        try:
            tree = Tree(tree_path, format=actual_tree_format)
        except FileNotFoundError:
            raise FileNotFoundError(f"Tree file not found at: {tree_path}")
        except Exception as e: # Catch other ete3 loading errors
            raise ValueError(f"Error loading tree from '{tree_path}' with format code {actual_tree_format}: {e}")


        # Load the chromosome count data
        try:
            # Pass through relevant kwargs to read_csv if provided
            read_csv_kwargs = {k: v for k, v in kwargs.items() if k in pd.read_csv.__code__.co_varnames}
            traits_df = pd.read_csv(counts_path, **read_csv_kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f"Counts file not found at: {counts_path}")
        except Exception as e: # Catch other pandas loading errors
            raise ValueError(f"Error loading counts data from '{counts_path}': {e}")

        # Validate required columns
        if species_col not in traits_df.columns:
            raise ValueError(
                f"Species column '{species_col}' not found in counts file '{counts_path}'. Available columns: {list(traits_df.columns)}"
            )
        if counts_col not in traits_df.columns:
            raise ValueError(
                f"Counts column '{counts_col}' not found in counts file '{counts_path}'. Available columns: {list(traits_df.columns)}"
            )

        # Prepare traits_df for validation and PhyloData creation
        try:
            # Avoid modifying original df if it's used elsewhere, though unlikely here
            processed_traits_df = traits_df.set_index(species_col)
        except KeyError:
            # This case should ideally be caught by the column check above, but as a fallback:
            raise ValueError(f"Species column '{species_col}' could not be set as index. Ensure it exists and contains unique identifiers.")


        # --- Data Validation ---
        tree_tips = set(tree.get_leaf_names())
        trait_species = set(processed_traits_df.index)

        if not tree_tips:
            raise ValueError("The phylogenetic tree has no leaf nodes.")
        if not trait_species: # Corrected check for an empty set
            raise ValueError(f"No species found in the counts file '{counts_path}' using species column '{species_col}'.")


        if tree_tips != trait_species:
            missing_in_tree = list(trait_species - tree_tips)
            missing_in_traits = list(tree_tips - trait_species)
            error_msg_parts = []
            if missing_in_tree:
                error_msg_parts.append(
                    f"Species in counts file but not in tree: {missing_in_tree}"
                )
            if missing_in_traits:
                error_msg_parts.append(
                    f"Species in tree but not in counts file: {missing_in_traits}"
                )
            raise ValueError(
                "Mismatch between tree tips and trait data: " + "; ".join(error_msg_parts)
            )

        # Ensure the dataframe is sorted in the same order as tree tips
        # This uses .loc which can raise KeyError if any names are missing,
        # but the check above should ensure all names are present.
        try:
            # Use only the counts_col for the PhyloData object's traits part
            ordered_traits = processed_traits_df.loc[tree.get_leaf_names(), [counts_col]]
        except KeyError as e:
            # Should not happen if the sets matched, but good to be defensive
            raise ValueError(f"Internal error: Could not align trait data with tree tips after validation. Missing key: {e}")


        phylo_data_object = PhyloData(tree=tree, traits=ordered_traits)
        # self.phylo_data_object = phylo_data_object # Store if DataLoader needs to hold state
        return phylo_data_object

    # Placeholder for a separate validation method if we decide to split it.
    # def validate_data(self, tree, counts_df, species_col='species'):
    #     """
    #     Validates that tree tips match species in the counts data.
    #     This logic is currently integrated into load_phylo_data.
    #     """
    #     # ... (validation logic as in load_phylo_data)
    #     pass

# Example Usage (optional, can be removed or kept for direct testing of DataLoader)
if __name__ == '__main__':
    from .config import DefaultConfig # For example config

    print("--- Testing DataLoader ---")

    # Create dummy files for testing
    dummy_tree_content = "((A:1,B:1):1,C:2);"
    dummy_counts_content = "species,count,other_info\nA,10,infoA\nB,12,infoB\nC,14,infoC"
    dummy_tree_file = "dummy_tree_for_loader.nwk"
    dummy_counts_file = "dummy_counts_for_loader.csv"

    with open(dummy_tree_file, "w") as f:
        f.write(dummy_tree_content)
    with open(dummy_counts_file, "w") as f:
        f.write(dummy_counts_content)

    # Test with default config
    data_loader = DataLoader(config=DefaultConfig())

    print("\n1. Testing successful load:")
    try:
        phylo_data = data_loader.load_phylo_data(dummy_tree_file, dummy_counts_file)
        print(f"Successfully loaded data. Tree: {phylo_data.tree.get_ascii(attributes=['name'])}")
        print(f"Traits:\n{phylo_data.traits}")
    except Exception as e:
        print(f"Error during successful load test: {e}")

    print("\n2. Testing with custom column names:")
    dummy_counts_custom_cols_content = "taxon_id,chromosome_val\nA,10\nB,12\nC,14"
    dummy_counts_custom_cols_file = "dummy_counts_custom.csv"
    with open(dummy_counts_custom_cols_file, "w") as f:
        f.write(dummy_counts_custom_cols_content)
    try:
        phylo_data_custom = data_loader.load_phylo_data(
            dummy_tree_file,
            dummy_counts_custom_cols_file,
            species_col="taxon_id",
            counts_col="chromosome_val"
        )
        print(f"Successfully loaded data with custom columns. Tree: {phylo_data_custom.tree.get_ascii(attributes=['name'])}")
        print(f"Traits (custom cols):\n{phylo_data_custom.traits}")
    except Exception as e:
        print(f"Error during custom column test: {e}")

    print("\n3. Testing mismatched data (species in counts not in tree):")
    dummy_counts_mismatch_content = "species,count\nA,10\nB,12\nD,14" # D is not in tree
    dummy_counts_mismatch_file = "dummy_counts_mismatch.csv"
    with open(dummy_counts_mismatch_file, "w") as f:
        f.write(dummy_counts_mismatch_content)
    try:
        data_loader.load_phylo_data(dummy_tree_file, dummy_counts_mismatch_file)
    except ValueError as e:
        print(f"Caught expected ValueError for mismatch: {e}")
    except Exception as e:
        print(f"Unexpected error during mismatch test: {e}")

    print("\n4. Testing file not found for tree:")
    try:
        data_loader.load_phylo_data("non_existent_tree.nwk", dummy_counts_file)
    except FileNotFoundError as e:
        print(f"Caught expected FileNotFoundError for tree: {e}")
    except Exception as e:
        print(f"Unexpected error during tree not found test: {e}")

    print("\n5. Testing file not found for counts:")
    try:
        data_loader.load_phylo_data(dummy_tree_file, "non_existent_counts.csv")
    except FileNotFoundError as e:
        print(f"Caught expected FileNotFoundError for counts: {e}")
    except Exception as e:
        print(f"Unexpected error during counts not found test: {e}")

    # Clean up dummy files
    import os
    os.remove(dummy_tree_file)
    os.remove(dummy_counts_file)
    os.remove(dummy_counts_custom_cols_file)
    os.remove(dummy_counts_mismatch_file)

    print("\n--- DataLoader tests complete ---")
