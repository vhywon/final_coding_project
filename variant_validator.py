"""
variant_validator.py

Provides functions to validate HGVS variants using the VariantValidator API.
"""

import requests  # Import requests for HTTP API calls
import json  # Import json for parsing API responses
import logging  # Import logging for tracking execution and errors
from requests.exceptions import Timeout, RequestException  # Specific exceptions for requests

logger = logging.getLogger(__name__)

def validate_variant_refseq(variant, genome_build):
    """Validates an HGVS variant using VariantValidator's RefSeq endpoint."""
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
    """Validates an HGVS variant using VariantValidator's Ensembl endpoint."""
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
    """Validates an HGVS variant using RefSeq first, then falls back to Ensembl if RefSeq fails."""
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