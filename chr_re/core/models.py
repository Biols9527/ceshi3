from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd

# The type for 'tree' can be refined if a single library is enforced,
# e.g., ete3.Tree or Bio.Phylo.BaseTree.Tree. For now, Any is flexible.
TreeObject = Any


@dataclass
class PhyloData:
    """
    A unified data container for phylogenetic analysis inputs.

    Attributes:
        tree: The phylogenetic tree object from libraries like ete3 or Biopython.
        traits: A DataFrame where the index matches the tree's tip names and
                columns represent different traits.
    """
    tree: TreeObject
    traits: pd.DataFrame


@dataclass
class AnalysisResult:
    """
    A unified data container for the results of a phylogenetic analysis.

    Attributes:
        annotated_tree: The phylogenetic tree, annotated with inferred data
                        like ancestral states.
        parameters: A dictionary of estimated model parameters, such as
                    evolutionary rates.
        likelihood: The log-likelihood of the model, if applicable.
        raw_output: The raw, unprocessed output from the analysis method,
                    useful for debugging or custom post-processing.
    """
    annotated_tree: TreeObject
    parameters: Dict[str, Any]
    likelihood: float | None = None
    raw_output: Any | None = None
