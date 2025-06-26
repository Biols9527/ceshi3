"""import pandas as pd
from ete3 import Tree

from .models import PhyloData


def load_phylo_data(
    tree_path: str,
    counts_path: str,
    tree_format: int = 0,
    species_col: str = "species",
    counts_col: str = "count",
) -> PhyloData:
    """
    Loads a phylogenetic tree and corresponding trait data into a unified
    PhyloData object.

    Args:
        tree_path: Path to the phylogenetic tree file (e.g., in Newick format).
        counts_path: Path to the CSV file containing trait data.
        tree_format: The format code for the tree file, as used by ete3.
                     Defaults to 0 (Newick).
        species_col: The name of the column in the CSV that contains species names.
        counts_col: The name of the column in the CSV that contains the trait counts.

    Returns:
        A PhyloData object containing the loaded tree and trait data.

    Raises:
        FileNotFoundError: If either the tree or counts file cannot be found.
        ValueError: If the species names in the tree and counts file do not match,
                    or if the specified columns are not in the CSV file.
    """
    # Load the phylogenetic tree
    try:
        tree = Tree(tree_path, format=tree_format)
    except FileNotFoundError:
        raise FileNotFoundError(f"Tree file not found at: {tree_path}")

    # Load the chromosome count data
    try:
        traits_df = pd.read_csv(counts_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Counts file not found at: {counts_path}")

    # Validate required columns
    if species_col not in traits_df.columns:
        raise ValueError(
            f"Species column '{species_col}' not found in counts file."
        )
    if counts_col not in traits_df.columns:
        raise ValueError(f"Counts column '{counts_col}' not found in counts file.")

    # Set the species column as the index to facilitate matching
    traits_df = traits_df.set_index(species_col)

    # --- Data Validation ---
    tree_tips = set(tree.get_leaf_names())
    trait_species = set(traits_df.index)

    if tree_tips != trait_species:
        missing_in_tree = trait_species - tree_tips
        missing_in_traits = tree_tips - trait_species
        error_msg = []
        if missing_in_tree:
            error_msg.append(
                f"Species in counts file but not in tree: {missing_in_tree}"
            )
        if missing_in_traits:
            error_msg.append(
                f"Species in tree but not in counts file: {missing_in_traits}"
            )
        raise ValueError("Mismatch between tree tips and trait data: " + "; ".join(error_msg))

    # Ensure the dataframe is sorted in the same order as tree tips (optional but good practice)
    ordered_traits = traits_df.loc[tree.get_leaf_names()]

    return PhyloData(tree=tree, traits=ordered_traits)
""
