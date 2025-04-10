import requests  # Import requests for HTTP API calls
import json  # Import json for parsing API responses
import logging  # Import logging for tracking execution and errors
from requests.exceptions import Timeout, RequestException  # Specific exceptions for requests

# Configure logging to write to a file with a detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("clinvar_validation.log")  # Log to a file named clinvar_validation.log
    ]
)
logger = logging.getLogger(__name__)  # Create a logger instance


def validate_variant_refseq(variant, genome_build):
    """Validate an HGVS variant using VariantValidator's RefSeq endpoint."""
    # Log the start of RefSeq validation
    logger.info(f"Validating variant '{variant}' with RefSeq endpoint for {genome_build}")
    # Define the base URL for VariantValidator's RefSeq API
    base_url = "https://rest.variantvalidator.org/VariantValidator/variantvalidator"
    # Construct the full URL with genome build and variant
    url = f"{base_url}/{genome_build}/{variant}/all?content-type=application%2Fjson"
    try:
        # Send GET request with a 10-second timeout to avoid hanging
        response = requests.get(url, timeout=10)
        # Raise an exception if the HTTP status indicates an error (e.g., 404, 500)
        response.raise_for_status()
        # Parse and return the JSON response
        validation_data = response.json()
        logger.info(f"Successfully validated '{variant}' with RefSeq endpoint")
        return validation_data
    except Timeout:
        # Handle timeout specifically
        logger.error(f"Timeout after 10 seconds validating '{variant}' with RefSeq endpoint")
        return None
    except RequestException as e:
        # Handle other HTTP-related errors
        logger.error(f"HTTP error validating '{variant}' with RefSeq: {e}")
        return None
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        logger.error(f"JSON decode error for RefSeq response of '{variant}': {e}")
        return None
    except Exception as e:
        # Catch any unexpected errors during validation
        logger.error(f"Unexpected error validating '{variant}' with RefSeq: {e}")
        return None


def validate_variant_ensembl(variant, genome_build):
    """Validate an HGVS variant using VariantValidator's Ensembl endpoint."""
    # Log the start of Ensembl validation
    logger.info(f"Validating variant '{variant}' with Ensembl endpoint for {genome_build}")
    # Define the base URL for VariantValidator's Ensembl API
    base_url = "https://rest.variantvalidator.org/VariantValidator/variantvalidator_ensembl"
    # Construct the full URL with genome build and variant
    url = f"{base_url}/{genome_build}/{variant}/all?content-type=application%2Fjson"
    try:
        # Send GET request with a 10-second timeout
        response = requests.get(url, timeout=10)
        # Raise an exception for HTTP errors
        response.raise_for_status()
        # Parse and return the JSON response
        validation_data = response.json()
        logger.info(f"Successfully validated '{variant}' with Ensembl endpoint")
        return validation_data
    except Timeout:
        # Handle timeout specifically
        logger.error(f"Timeout after 10 seconds validating '{variant}' with Ensembl endpoint")
        return None
    except RequestException as e:
        # Handle other HTTP-related errors
        logger.error(f"HTTP error validating '{variant}' with Ensembl: {e}")
        return None
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        logger.error(f"JSON decode error for Ensembl response of '{variant}': {e}")
        return None
    except Exception as e:
        # Catch any unexpected errors during validation
        logger.error(f"Unexpected error validating '{variant}' with Ensembl: {e}")
        return None


def validate_hgvs_variant(variant, genome_build):
    """Validate an HGVS variant by trying RefSeq then Ensembl endpoints."""
    # Log the start of the validation process
    logger.info(f"Starting validation for HGVS variant '{variant}' with {genome_build}")
    # Try RefSeq validation first
    validation_result = validate_variant_refseq(variant, genome_build)
    # Check if RefSeq validation succeeded and variant is not flagged as an error
    if validation_result and 'flag' in validation_result and validation_result['flag'] != 'error':
        logger.info(f"Variant '{variant}' validated successfully as RefSeq")
        return validation_result

    # If RefSeq fails or flags an error, try Ensembl
    logger.info(f"RefSeq validation failed or invalid, attempting Ensembl for '{variant}'")
    validation_result = validate_variant_ensembl(variant, genome_build)
    # Check if Ensembl validation succeeded and variant is not flagged as an error
    if validation_result and 'flag' in validation_result and validation_result['flag'] != 'error':
        logger.info(f"Variant '{variant}' validated successfully as Ensembl")
        return validation_result

    # Log failure if neither endpoint validates the variant
    logger.warning(f"Variant '{variant}' could not be validated by RefSeq or Ensembl")
    return None


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
        dict: A dictionary with germline_classification, clinical_impact_classification,
              and oncogenicity_classification.
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


def main():
    """Main function to validate an HGVS variant and fetch ClinVar data."""
    # Log the start of the program
    logger.info("Starting ClinVar search program")
    try:
        # Prompt user for HGVS variant and remove whitespace
        hgvs_variant = input(
            "Enter the HGVS variant (e.g., NM_000518.5:c.92+1G>A): ").strip()
        # Prompt user for genome build and convert to uppercase
        genome_build = input("Enter the genome build (GRCh38 or GRCh37): ").strip().upper()
        logger.info(f"User input - HGVS variant: '{hgvs_variant}', Genome build: '{genome_build}'")

        # Validate user inputs
        if not hgvs_variant:
            logger.error("No HGVS variant provided")
            raise ValueError("No HGVS variant provided")
        if genome_build not in ["GRCH38", "GRCH37"]:
            logger.error(f"Invalid genome build: {genome_build}")
            raise ValueError("Genome build must be GRCh38 or GRCh37")

        # Validate the HGVS variant using VariantValidator
        validation_result = validate_hgvs_variant(hgvs_variant, genome_build)

        # Check if validation failed
        if not validation_result:
            logger.error(f"Validation failed for '{hgvs_variant}'")
            print(f"Error: The entered variant '{hgvs_variant}' is not valid according to VariantValidator.")
            return

        # Log and inform user of successful validation
        logger.info(f"Validation successful for '{hgvs_variant}'")
        print(
            f"HGVS variant '{hgvs_variant}' validated successfully for {genome_build}. Proceeding to ClinVar search...")

        # Query ClinVar with the validated variant
        clinvar_results = search_clinvar_by_hgvs(hgvs_variant)

        # Check if ClinVar returned valid results
        if clinvar_results and 'result' in clinvar_results and clinvar_results['result'] and 'uids' in clinvar_results[
            'result']:
            # Extract the first UID and its data
            result_uid = clinvar_results['result']['uids'][0]
            result_data = clinvar_results['result'].get(result_uid, {})
            logger.debug(f"ClinVar result UID: {result_uid}, Data: {result_data}")

            # Extract classifications from the result data
            classifications = extract_classifications(result_data, result_uid)
            if classifications is None:
                logger.error(f"Failed to extract classifications for '{hgvs_variant}'")
                print("Error: Failed to extract classifications from ClinVar data.")
                return

            # Display ClinVar results to the user
            print(f"\nClinVar Results for HGVS variant '{hgvs_variant}' (UID: {classifications['uid']}):")
            print(f"Germline Classification: {classifications['germline_classification']}")
            print(f"Clinical Impact Classification: {classifications['clinical_impact_classification']}")
            print(f"Oncogenicity Classification: {classifications['oncogenicity_classification']}")
            logger.info(f"Successfully displayed ClinVar results for '{hgvs_variant}'")
        else:
            # Inform user if no ClinVar results were found
            logger.info(f"No ClinVar results found for '{hgvs_variant}'")
            print(f"No results found for HGVS variant '{hgvs_variant}' in ClinVar.")

    except ValueError as e:
        # Handle input validation errors
        logger.error(f"Input error: {e}")
        print(f"Input error: {e}")
    except KeyboardInterrupt:
        # Handle user termination (e.g., Ctrl+C)
        logger.info("Program terminated by user")
        print("\nProgram terminated by user.")
    except Exception as e:
        # Handle unexpected errors in main execution
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")
    finally:
        # Log the end of the program execution
        logger.info("ClinVar search program completed")


if __name__ == "__main__":
    # Run the main function if the script is executed directly
    main()