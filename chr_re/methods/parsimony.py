"""from ..core.models import PhyloData, AnalysisResult
from .base import BaseMethod


class ParsimonyMethod(BaseMethod):
    """
    Implements parsimony-based ancestral state reconstruction, adhering to the
    BaseMethod interface.
    """

    def _fitch(self, tree, traits):
        """Performs Fitch's algorithm."""
        parsimony_score = 0

        # First pass: post-order traversal (from tips to root)
        for node in tree.traverse("postorder"):
            if node.is_leaf():
                tip_name = node.name
                state = traits.loc[tip_name].iloc[0] # Get the first trait value
                node.add_feature("states", {state})
            else:
                # Union of child states for nodes with one child
                if len(node.children) == 1:
                    child_states = node.children[0].states
                    node.add_feature("states", child_states)
                else: # Intersection for nodes with two or more children
                    child_states_sets = [child.states for child in node.children]
                    intersection = set.intersection(*child_states_sets)
                    if intersection:
                        node.add_feature("states", intersection)
                    else:
                        union = set.union(*child_states_sets)
                        node.add_feature("states", union)
                        parsimony_score += 1

        # Second pass: pre-order traversal (from root to tips)
        for node in tree.traverse("preorder"):
            if node.is_root():
                # For the root, just pick one state if multiple are possible
                node.add_feature("state", list(node.states)[0])
            else:
                parent_state = node.up.state
                if parent_state in node.states:
                    node.add_feature("state", parent_state)
                else:
                    # If parent state is not in the possible set, pick one
                    node.add_feature("state", list(node.states)[0])
        
        return tree, parsimony_score

    def run(self, data: PhyloData, config: dict | None = None) -> AnalysisResult:
        """
        Executes the parsimony analysis using a specified algorithm.
        """
        if config is None or "algorithm" not in config:
            raise ValueError(
                "An algorithm (e.g., 'Fitch', 'Sankoff') must be specified in the config."
            )

        algorithm = config["algorithm"]
        print(f"Running Parsimony analysis with algorithm: {algorithm}")

        # Make a deep copy of the tree to avoid modifying the original data object
        tree_copy = data.tree.copy("newick-extended")

        if algorithm == "Fitch":
            annotated_tree, score = self._fitch(tree_copy, data.traits)
            return AnalysisResult(
                annotated_tree=annotated_tree,
                parameters={"parsimony_score": score, "model_name": "Fitch Parsimony"},
                likelihood=None  # Parsimony does not have a likelihood
            )
        elif algorithm == "Sankoff":
            if "cost_matrix" not in config:
                raise ValueError("Sankoff algorithm requires a 'cost_matrix' in the config.")
            raise NotImplementedError("Sankoff algorithm not implemented yet.")
        else:
            raise ValueError(f"Unsupported parsimony algorithm: {algorithm}")
"""
