"""
Description:
This Python script is a command-line tool for validating HGVS (Human Genome Variation Society) variants and
retrieving related classification data from NCBI ClinVar.
**************
Main entry point for the HGVS variant classification tool.

This script coordinates input collection, variant validation, ClinVar query, and final output.
It uses external modules:
- variant_validator.py for HGVS variant validation
- clinvar.py for ClinVar querying and classification extraction
- output.py for gene symbol extraction and formatting

Logging is enabled to 'clinvar_validation.log' with rotating file support.
Run via: python main.py

**************
"""

import logging  # Import logging for tracking execution and errors
from requests.exceptions import Timeout, RequestException # Specific exceptions for requests
from logging.handlers import RotatingFileHandler
from variant_validator import validate_hgvs_variant
from clinvar import search_clinvar_by_hgvs, extract_classifications
from output import extract_gene_symbol, format_results


# Configure logging to use RotatingFileHandler with detailed format
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

rotating_handler = RotatingFileHandler(
"clinvar_validation.log",   # Log file name
    maxBytes=5 * 1024 * 1024,   # 5 MB file size limit
    backupCount=3               # Keep 3 backup log files
)
rotating_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(rotating_handler)


def main():
    """Main function to validate an HGVS variant and fetch ClinVar data.
    The user input as a HGVS variant and genome assembly build (GRCh38/GRCh37)"""
    # Log the start of the program
    logger.info("Starting ClinVar search program")
    try:
        # Prompt user for HGVS variant and remove whitespace
        hgvs_variant = input("Enter the HGVS variant (e.g., NM_000518.5:c.92+1G>A): ").strip()
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

        # Step 1: Validate the HGVS variant using VariantValidator
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

        # Step 2: Extract gene symbol from VV response
        gene_symbol = extract_gene_symbol(validation_result)
        if not gene_symbol:
            logger.warning(f"No gene symbol found for '{hgvs_variant}'")
            print("Gene Symbol: Not available — the variant may be intronic or unrecognized by transcript")
            gene_symbol = "N/A"
        else:
            print(f"Gene Symbol: {gene_symbol}")

        # Step 3: Query ClinVar with the validated variant
        clinvar_results = search_clinvar_by_hgvs(hgvs_variant)

        print("\nRaw ClinVar results:")
        import pprint
        pprint.pprint(clinvar_results)

        # Check if ClinVar returned valid results
        if clinvar_results and 'result' in clinvar_results and clinvar_results['result'] and 'uids' in clinvar_results[
            'result']:
            # Extract the first UID and its data
            result_uid = clinvar_results['result']['uids'][0]
            result_data = clinvar_results['result'].get(result_uid, {})
            logger.debug(f"ClinVar result UID: {result_uid}, Data: {result_data}")

            # Extract classifications from the result data
            classifications = extract_classifications(result_data, result_uid)
            print("\nExtracted classifications:")
            import pprint
            pprint.pprint(classifications)

            if classifications is None:
                logger.error(f"Failed to extract classifications for '{hgvs_variant}'")
                print("Error: Failed to extract classifications from ClinVar data.")
                return
            # Step 4: Format output
            result_summary = format_results(gene_symbol, classifications)
            print("\nFinal Output Summary:")
            for key, value in result_summary.items():
                print(f"{key.capitalize().replace('_', ' ')}: {value}")

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