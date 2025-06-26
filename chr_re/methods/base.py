from abc import ABC, abstractmethod

from ..core.models import PhyloData, AnalysisResult


class BaseMethod(ABC):
    """
    Abstract base class for all phylogenetic analysis methods.

    This class defines the common interface that all analysis methods (like
    Maximum Likelihood, Bayesian, Parsimony) must implement. This ensures
    that the core pipeline can treat them interchangeably.
    """

    @abstractmethod
    def run(self, data: PhyloData, config: dict | None = None) -> AnalysisResult:
        """
        Execute the analysis.

        Args:
            data: A PhyloData object containing the tree and trait data.
            config: A dictionary containing configuration options specific
                    to the analysis method.

        Returns:
            An AnalysisResult object containing the results of the analysis.
        """
        pass
