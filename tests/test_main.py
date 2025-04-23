""" unit tests for main.py """

import unittest
from unittest.mock import patch, Mock
import json
import requests
from variant_tool.clinvar import search_clinvar_by_hgvs


class TestSearchClinvarByHgvs(unittest.TestCase):

    def setUp(self):
        # Set up mock responses used across multiple tests
        # Mock successful search response with one result
        self.success_search_response = {
            "esearchresult": {
                "count": "1",
                "webenv": "NCID_1_123",
                "querykey": "1"
            }
        }
        # Mock successful summary response with variant details
        self.success_summary_response = {
            "result": {
                "uids": ["12345"],
                "12345": {"title": "Variant Data"}
            }
        }
        # Mock search response with no results
        self.empty_search_response = {
            "esearchresult": {
                "count": "0"
            }
        }

    def test_valid_hgvs_variant_success(self):
        # Test successful API call with valid HGVS variant
        with patch('requests.get') as mock_get:  # Mock the requests.get function
            # Configure mock for search request
            mock_search_response = Mock()
            mock_search_response.status_code = 200  # Simulate successful HTTP response
            mock_search_response.json.return_value = self.success_search_response
            # Configure mock for summary request
            mock_summary_response = Mock()
            mock_summary_response.status_code = 200  # Simulate successful HTTP response
            mock_summary_response.json.return_value = self.success_summary_response
            # Simulate two API calls: search then summary
            mock_get.side_effect = [mock_search_response, mock_summary_response]

            result = search_clinvar_by_hgvs("NM_000518.5:c.92+1G>A")  # Call function with valid input
            self.assertIsNotNone(result)  # Check that a result is returned
            self.assertIn("result", result)  # Verify result contains expected key
            self.assertEqual(result["result"]["uids"], ["12345"])  # Check specific data
            mock_get.assert_called()  # Ensure API was "called"

    def test_empty_hgvs_variant(self):
        # Test input validation for empty or whitespace-only strings
        with self.assertRaises(ValueError):  # Expect ValueError to be raised
            search_clinvar_by_hgvs("")  # Empty string should fail

        with self.assertRaises(ValueError):  # Expect ValueError to be raised
            search_clinvar_by_hgvs("   ")  # Whitespace-only string should fail

    def test_non_string_hgvs_variant(self):
        # Test input validation for non-string inputs
        with self.assertRaises(ValueError):  # Expect ValueError to be raised
            search_clinvar_by_hgvs(123)  # Integer should fail

        with self.assertRaises(ValueError):  # Expect ValueError to be raised
            search_clinvar_by_hgvs(None)  # None should fail

    def test_no_results_found(self):
        # Test handling when no results are found in ClinVar
        with patch('requests.get') as mock_get:  # Mock the requests.get function
            mock_response = Mock()
            mock_response.status_code = 200  # Simulate successful HTTP response
            mock_response.json.return_value = self.empty_search_response  # No results
            mock_get.return_value = mock_response  # Return mock response

            result = search_clinvar_by_hgvs("NM_000518.5:c.9999G>T")  # Call with variant
            self.assertIsNone(result)  # Expect None when no results
            mock_get.assert_called_once()  # Ensure API was called exactly once

    def test_request_timeout(self):
        # Test handling of request timeout
        with patch('requests.get', side_effect=requests.exceptions.Timeout):  # Simulate timeout
            with patch('builtins.print') as mock_print:  # Mock print to capture output
                result = search_clinvar_by_hgvs("NM_000518.5:c.92+1G>A")  # Call function
                self.assertIsNone(result)  # Expect None on timeout
                mock_print.assert_called_once_with(
                    "Request timed out after 10 seconds for HGVS variant: NM_000518.5:c.92+1G>A"
                )  # Verify error message

    def test_request_exception(self):
        # Test handling of general request exceptions
        with patch('requests.get', side_effect=requests.exceptions.RequestException("Network Error")):  # Simulate error
            with patch('builtins.print') as mock_print:  # Mock print to capture output
                result = search_clinvar_by_hgvs("NM_000518.5:c.92+1G>A")  # Call function
                self.assertIsNone(result)  # Expect None on error
                mock_print.assert_called_once_with(
                    "Error during ClinVar API request for HGVS variant 'NM_000518.5:c.92+1G>A': Network Error"
                )  # Verify error message

    def test_json_decode_error(self):
        # Test handling of JSON decode errors
        with patch('requests.get') as mock_get:  # Mock the requests.get function
            mock_response = Mock()
            mock_response.status_code = 200  # Simulate successful HTTP response
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)  # Simulate JSON error
            mock_get.return_value = mock_response  # Return mock response

            with patch('builtins.print') as mock_print:  # Mock print to capture output
                result = search_clinvar_by_hgvs("NM_000518.5:c.92+1G>A")  # Call function
                self.assertIsNone(result)  # Expect None on JSON error
                mock_print.assert_called_once_with(
                    "Error decoding JSON response for HGVS variant 'NM_000518.5:c.92+1G>A': Invalid JSON: line 1 column 1 (char 0)"
                )  # Verify full error message


if __name__ == '__main__':
    unittest.main()  # Run the tests when script is executed directly