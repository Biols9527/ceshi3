from ..core.models import PhyloData, AnalysisResult
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
                # Assuming traits is a DataFrame with species as index and a single column for counts
                state = traits.loc[tip_name].iloc[0]
                node.add_feature("states", {state})
            else:
                child_states_sets = [child.states for child in node.children]
                if not child_states_sets: # Should not happen in a valid tree structure for internal nodes
                    node.add_feature("states", set())
                    continue

                if len(node.children) == 1: # Handle nodes with a single child (e.g. unary nodes)
                    node.add_feature("states", child_states_sets[0])
                else: # Nodes with two or more children
                    intersection = set.intersection(*child_states_sets)
                    if intersection:
                        node.add_feature("states", intersection)
                    else:
                        union = set.union(*child_states_sets)
                        node.add_feature("states", union)
                        parsimony_score += 1

        # Second pass: pre-order traversal (from root to tips)
        # Ensure root has a state assigned before children try to access node.up.state
        if tree.children: # Check if tree is not just a single node
            # Assign state to root first if it's not a leaf
            if not tree.is_leaf():
                 # If root's states is empty (e.g. from an empty tree or problematic first pass), handle it.
                if not hasattr(tree, 'states') or not tree.states:
                     # Fallback: if states are not determined, assign a default or raise error
                     # For now, let's assign an arbitrary state if possible or skip if no states
                     # This part might need more robust handling depending on expected inputs
                    pass # Or tree.add_feature("state", some_default_if_no_states_determined)
                else:
                    tree.add_feature("state", list(tree.states)[0])

        for node in tree.traverse("preorder"):
            # Root state is already handled or node is a leaf
            if node.is_root() or node.is_leaf():
                if node.is_leaf() and not hasattr(node, "state"): # Ensure leaves have their state from traits
                    tip_name = node.name
                    state_val = traits.loc[tip_name].iloc[0]
                    node.add_feature("state", state_val) # Assign the actual state value
                continue # Skip root and leaves for parent-dependent assignment logic below

            if not node.up: # Should not happen for non-root nodes in preorder after root
                continue

            # Parent state should exist from previous step in pre-order or root assignment
            if not hasattr(node.up, "state"):
                # This indicates an issue with state assignment order or tree structure
                # Potentially assign a fallback or log a warning/error
                # For now, if parent state is missing, we can't determine child state based on it
                # A simple choice is to pick from its own states, if available and not parent-derived
                if hasattr(node, 'states') and node.states: # Check if node.states exists
                    node.add_feature("state", list(node.states)[0])
                # else: node remains without a specific "state" if states were also empty.
                continue

            parent_state = node.up.state
            if hasattr(node, 'states') and node.states: # Check if node.states exists
                if parent_state in node.states:
                    node.add_feature("state", parent_state)
                else:
                    node.add_feature("state", list(node.states)[0])
            elif hasattr(node, 'states') and not node.states: # states attribute exists but is empty
                 # If states set is empty, cannot pick; could inherit parent or specific logic
                 node.add_feature("state", parent_state) # Example: inherit parent if own set is empty
            # If node.states does not exist (e.g. leaf processed differently), it might already have 'state'
            # or this logic path might need refinement depending on how leaves are handled initially.
            # The leaf check at the start of the loop should manage leaves.

        return tree, parsimony_score

    def run(self, data: PhyloData, config: dict | None = None) -> AnalysisResult:
        """
        Executes the parsimony analysis using a specified algorithm.
        """
        if config is None:
            config = {} # Default to empty config if None

        algorithm = config.get("algorithm", "Fitch") # Default to Fitch if not specified

        print(f"Running Parsimony analysis with algorithm: {algorithm}")

        # Make a deep copy of the tree to avoid modifying the original PhyloData tree
        # ETE3's copy method with "newick-extended" should preserve features if they were newick compatible
        # For full feature preservation, a more robust deepcopy of the ETE tree object might be needed
        # if features are complex Python objects. tree.copy() is generally good.
        tree_copy = data.tree.copy("newick-extended") # Using newick-extended to try and keep annotations

        if algorithm.lower() == "fitch":
            # Ensure traits are passed to _fitch as it expects
            annotated_tree, score = self._fitch(tree_copy, data.traits)
            return AnalysisResult(
                annotated_tree=annotated_tree,
                parameters={"parsimony_score": score, "model_name": "Fitch Parsimony"},
                likelihood=None  # Parsimony does not have a likelihood
            )
        elif algorithm.lower() == "sankoff":
            if "cost_matrix" not in config:
                raise ValueError("Sankoff algorithm requires a 'cost_matrix' in the config.")
            # Placeholder for Sankoff implementation
            raise NotImplementedError("Sankoff algorithm not implemented yet.")
        else:
            raise ValueError(f"Unsupported parsimony algorithm: {algorithm}")
