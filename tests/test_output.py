"""
Unit tests for output.py

This test suite checks:
- The structure of format_results()
- That pretty_print_results() runs without error using a sample input

Note: These are functional display tests, not visual output verification.
"""
import sys
import os

# Add the parent directory (project root) to sys.path so 'output.py' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from output import format_results, pretty_print_results

class TestOutputFormatting(unittest.TestCase):

    def test_format_results_structure(self):
        """Test that format_results returns expected dictionary keys."""
        gene = "TP53"
        classifications = {
            "uid": "7890",
            "germline_classification": {"description": "Pathogenic"},
            "clinical_impact_classification": {"description": "Moderate"},
            "oncogenicity_classification": {"description": "Likely oncogenic"}
        }
        result = format_results(gene, classifications)
        self.assertEqual(result["gene"], "TP53")
        self.assertIn("variant_uid", result)
        self.assertIn("germline", result)
        self.assertIn("clinical_impact", result)
        self.assertIn("oncogenicity", result)

    def test_pretty_print_results_runs(self):
        """Ensure pretty_print_results executes without error."""
        summary = {
            "gene": "TP53",
            "variant_uid": "7890",
            "germline": {"description": "Pathogenic"},
            "clinical_impact": {"description": "Moderate"},
            "oncogenicity": {"description": "Likely oncogenic"}
        }
        pretty_print_results(summary)  # Should not raise exceptions

if __name__ == '__main__':
    unittest.main()
