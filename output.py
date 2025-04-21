"""
output.py

Handles formatting and display of variant classification results.
"""

import logging

logger = logging.getLogger(__name__)

def extract_gene_symbol(validation_response):
    """
    Extracts the gene symbol from the VariantValidator response.

    This function handles:
    1. Standard responses where the top-level key is the HGVS string
    2. Warning responses where gene info is under 'validation_warning_1'

      Returns
    -------
    str or None
        The gene symbol (e.g., 'HBB', 'BRCA2'), or None if not found.

     Notes
    -----
    - Gene symbol may not be available for intronic variants or those with validation warnings.
    - If VariantValidator can't resolve a transcript, gene_symbol may be an empty string.
    - Always handle None as a fallback in the main program.
    """
    try:
        # Case 1: top-level HGVS key (most common structure)
        for key, val in validation_response.items():
            if isinstance(val, dict) and 'gene_symbol' in val and val['gene_symbol']:
                gene_symbol = val['gene_symbol']
                logger.info(f"Extracted gene symbol from key '{key}': {gene_symbol}")
                return gene_symbol

        # Case 2: warning-based response (e.g. under 'validation_warning_1')
        warning_block = validation_response.get('validation_warning_1', {})
        if 'gene_symbol' in warning_block and warning_block['gene_symbol']:
            gene_symbol = warning_block['gene_symbol']
            logger.info(f"Extracted gene symbol from 'validation_warning_1': {gene_symbol}")
            return gene_symbol

        # If none found
        logger.warning("Gene symbol not found in standard or warning response")
    except Exception as e:
        logger.error(f"Error extracting gene symbol: {e}")
    return None
