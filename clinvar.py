"""
clinvar.py

Hclinvar.py

Queries the NCBI ClinVar database using an HGVS variant string to extract clinical classifications.

Functions:
- search_clinvar_by_hgvs(): Uses eSearch + eSummary API calls to retrieve variant summary data
- extract_classifications(): Extracts germline, clinical impact, and oncogenicity classifications

Handles input validation, timeout handling, request errors, and logs activity to clinvar_validation.log.

"""

import requests  # Import requests for HTTP API calls
import json  # Import json for parsing API responses
import logging  # Import logging for tracking execution and errors
from requests.exceptions import Timeout, RequestException  # Specific exceptions for requests

logger = logging.getLogger(__name__)

def search_clinvar_by_hgvs(hgvs_variant):
    """
    Queries the NCBI ClinVar API for a given HGVS variant and returns the results.

    Args:
        hgvs_variant (str): The HGVS variant string to search for (e.g., 'NM_000518.5:c.92+1G>A').

    Returns:
        dict or None: A dictionary containing the JSON response from the ClinVar API if successful,
                     or None if an error occurs or no results are found.

    Raises:
        ValueError: If hgvs_variant is empty or not a string.
    """

def search_clinvar_by_hgvs(hgvs_variant):
    """
    Queries the NCBI ClinVar API for a given HGVS variant and returns the results.

    Args:
        hgvs_variant (str): The HGVS variant string to search for (e.g., 'NM_000518.5:c.92+1G>A').

    Returns:
        dict or None: A dictionary containing the JSON response from the ClinVar API if successful,
                     or None if an error occurs or no results are found.

    Raises:
        ValueError: If hgvs_variant is empty or not a string.
    """
    # Validate that the input is a non-empty string
    if not isinstance(hgvs_variant, str) or not hgvs_variant.strip():
        logger.error("HGVS variant must be a non-empty string")
        raise ValueError("HGVS variant must be a non-empty string")

    # Log the start of the ClinVar search
    logger.info(f"Searching ClinVar for HGVS variant '{hgvs_variant}'")
    # Define the base URL for ClinVar's eSearch API
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    # Set up parameters for the eSearch request
    params = {
        'db': 'clinvar',  # Specify ClinVar database
        'term': f'"{hgvs_variant.strip()}"[hgvs]',  # Search for exact HGVS match
        'retmode': 'json',  # Request JSON response
        'retmax': 1,  # Limit to 1 result
        'usehistory': 'y'  # Enable history for detailed fetch
    }

    try:
        # Send GET request to search ClinVar IDs
        response = requests.get(base_url, params=params, timeout=10)
        # Raise exception for HTTP errors
        response.raise_for_status()
        # Parse the JSON response
        search_data = response.json()
        logger.debug(f"ClinVar eSearch response: {search_data}")

        # Check if any results were found
        if 'esearchresult' not in search_data or int(search_data['esearchresult']['count']) == 0:
            logger.info(f"No ClinVar results found for '{hgvs_variant}'")
            return None

        # Extract WebEnv and QueryKey for detailed fetch
        webenv = search_data['esearchresult']['webenv']
        query_key = search_data['esearchresult']['querykey']
        logger.debug(f"WebEnv: {webenv}, QueryKey: {query_key}")

        # Define the base URL for ClinVar's eSummary API
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        # Set up parameters for eSummary request
        summary_params = {
            'db': 'clinvar',  # Specify ClinVar database
            'query_key': query_key,  # Reference the search result
            'WebEnv': webenv,  # Use history token
            'retmode': 'json',  # Request JSON response
            'retmax': 1  # Limit to 1 result
        }

        # Fetch detailed summary data
        summary_response = requests.get(summary_url, params=summary_params, timeout=10)
        # Raise exception for HTTP errors
        summary_response.raise_for_status()
        # Parse the JSON response
        summary_data = summary_response.json()
        logger.info(f"Successfully retrieved ClinVar data for '{hgvs_variant}'")
        logger.debug(f"ClinVar eSummary response: {summary_data}")

        # Return summary data if it contains results, otherwise None
        return summary_data if 'result' in summary_data else None

    except Timeout:
        # Handle ClinVar request timeout
        logger.error(f"ClinVar request timed out after 10 seconds for '{hgvs_variant}'")
        print(f"Request timed out after 10 seconds for HGVS variant: {hgvs_variant}")
        return None
    except RequestException as e:
        # Handle other ClinVar HTTP errors
        logger.error(f"ClinVar API request error for '{hgvs_variant}': {e}")
        print(f"Error during ClinVar API request for HGVS variant '{hgvs_variant}': {e}")
        return None
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors from ClinVar response
        logger.error(f"JSON decode error in ClinVar response for '{hgvs_variant}': {e}")
        print(f"Error decoding JSON response for HGVS variant '{hgvs_variant}': {e}")
        return None
    except Exception as e:
        # Handle unexpected errors in ClinVar search
        logger.error(f"Unexpected error searching ClinVar for '{hgvs_variant}': {e}")
        print(f"An unexpected error occurred while searching ClinVar: {e}")
        return None


def extract_classifications(result_data, uid):
    """
    Extracts specific classification details from ClinVar JSON result.

    Args:
        result_data (dict): The JSON data for a specific ClinVar result.
        uid (str): The unique identifier for the result.

    Returns:
        dict: A dictionary with germline_classification, clinical_impact_classification,and oncogenicity_classification.
    """
    # Log the start of classification extraction
    logger.info(f"Extracting classifications for UID: {uid}")
    try:
        # Extract clinical significance, defaulting to empty dict if not present
        clinical_significance = result_data.get('clinical_significance', {})
        # Extract germline classification with fallback message
        germline_classification = result_data.get('germline_classification', 'No germline classification available')
        # Extract clinical impact classification with fallback message
        clinical_impact = result_data.get('clinical_impact_classification',
                                          'No clinical impact classification available')
        # Extract oncogenicity classification with fallback message
        oncogenicity_classification = result_data.get('oncogenicity_classification',
                                                      'No oncogenicity classification available')

        # Construct and return the classifications dictionary
        classifications = {
            'uid': uid,
            'clinical_significance': clinical_significance,
            'germline_classification': germline_classification,
            'clinical_impact_classification': clinical_impact,
            'oncogenicity_classification': oncogenicity_classification
        }
        logger.debug(f"Classifications extracted: {classifications}")
        return classifications
    except KeyError as e:
        # Handle missing keys in result_data
        logger.error(f"Key error extracting classifications for UID {uid}: {e}")
        print(f"Error: Missing expected key in ClinVar data for UID {uid}: {e}")
        return None
    except Exception as e:
        # Handle unexpected errors during extraction
        logger.error(f"Unexpected error extracting classifications for UID {uid}: {e}")
        print(f"An unexpected error occurred while extracting classifications: {e}")
        return None
