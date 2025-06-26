"""Functions for detecting significant evolutionary events on a phylogenetic tree.
"""

from ..core.models import AnalysisResult


def detect_significant_events(result: AnalysisResult, config: dict | None = None) -> list:
    """
    Detects significant evolutionary events (e.g., large jumps in character value)
    on a tree that has been annotated with ancestral states.

    Args:
        result: The AnalysisResult object from a completed analysis run. This
                result must contain an 'annotated_tree'.
        config: A dictionary for any additional configuration, such as the
                threshold for what constitutes a 'significant' event.

    Returns:
        A list of dictionaries, where each dictionary describes a detected event.

    Raises:
        ValueError: If the result object does not contain an annotated tree.
    """
    print("Detecting significant evolutionary events...")

    if result.annotated_tree is None:
        raise ValueError("Event detection requires an annotated tree in the AnalysisResult.")

    # Default configuration for event detection
    if config is None:
        config = {}
    threshold = config.get("change_threshold", 5) # e.g., detect jumps of 5 or more chromosomes

    print(f"Using a change threshold of: {threshold}")

    # In a real implementation, you would traverse the annotated tree,
    # compare the reconstructed state of a parent node to its child node,
    # and if the change exceeds the threshold, record it as an event.

    # For example:
    # events = []
    # for node in result.annotated_tree.traverse("preorder"):
    #     if not node.is_root():
    #         parent_state = node.up.get_ancestral_state() # Fictional method
    #         child_state = node.get_ancestral_state()
    #         change = abs(child_state - parent_state)
    #         if change >= threshold:
    #             events.append({
    #                 "node": node.name,
    #                 "branch_length": node.dist,
    #                 "parent_state": parent_state,
    #                 "child_state": child_state,
    #                 "change": change
    #             })
    # return events

    # For now, we return a placeholder message.
    print("Event detection algorithm is not yet implemented.")
    return [
        {
            "placeholder": True,
            "message": "Algorithm not implemented. Would have searched for changes > threshold.",
        }
    ]


# Example of how to use this analysis module:
if __name__ == '__main__':
    from ..core.models import AnalysisResult

    print("--- Example Event Detection ---")

    # 1. Create a dummy AnalysisResult that contains an annotated tree
    #    In a real scenario, this tree would be an ete3.Tree object with custom attributes.
    class DummyAnnotatedTree:
        def __init__(self):
            self.name = "root"
        def __str__(self):
            return "A dummy annotated tree object"

    good_result = AnalysisResult(
        annotated_tree=DummyAnnotatedTree(),
        parameters={"some_param": 1},
        likelihood=-50.0
    )

    print("\nAnalyzing a result with an annotated tree:")
    try:
        events = detect_significant_events(good_result, config={"change_threshold": 3})
        print(f"--> Detected events: {events}")
    except ValueError as e:
        print(f"Caught unexpected error: {e}")


    # 2. Create a dummy result WITHOUT an annotated tree
    bad_result = AnalysisResult(
        annotated_tree=None,
        parameters={"some_param": 1},
        likelihood=-50.0
    )

    print("\nAnalyzing a result without an annotated tree (expected to fail):")
    try:
        events = detect_significant_events(bad_result)
        print(f"--> Detected events: {events}")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    print("\nEvent detection structure implemented.")
"""