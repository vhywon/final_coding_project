"""
output.py

This module handles:
- Extraction of gene symbol from VariantValidator response.
- Formatting and pretty-printing of final results from ClinVar classification.

Includes handling of standard and warning variant validation responses.
"""

def extract_gene_symbol(validation_result):
    """
    Attempts to extract gene symbol from validation result.

    Args:
        validation_result (dict): VariantValidator JSON response

    Returns:
        str: Extracted gene symbol or None
    """
    try:
        # If standard format
        for k in validation_result:
            record = validation_result[k]
            if isinstance(record, dict) and 'gene_symbol' in record:
                return record['gene_symbol']
        # If fallback warning format
        if 'validation_warning_1' in validation_result:
            warning_block = validation_result['validation_warning_1']
            if 'gene_symbol' in warning_block:
                return warning_block['gene_symbol']
    except Exception:
        return None
    return None


def format_results(gene_symbol, classifications):
    """
    Formats gene symbol and classification dictionary into a readable structure.

    Args:
        gene_symbol (str): Symbol like "HBB"
        classifications (dict): Output from extract_classifications

    Returns:
        dict: Formatted dictionary with user-friendly keys and values
    """
    return {
        "gene": gene_symbol,
        "variant_uid": classifications.get("uid"),
        "germline": classifications.get("germline_classification"),
        "clinical_impact": classifications.get("clinical_impact_classification"),
        "oncogenicity": classifications.get("oncogenicity_classification")
    }


def pretty_print_results(results):
    """
    Nicely formats and prints the result summary returned by format_results().

    Args:
        results (dict): Formatted dictionary with keys like 'gene', 'germline', etc.
    """
    print("\nClinical Variant Summary")
    print("=" * 40)
    print(f"Gene: {results.get('gene', 'N/A')}")
    print(f"Variant UID: {results.get('variant_uid', 'N/A')}\n")

    # Helper to format classification sections
    def print_section(title, data):
        print(f"{title}")
        if not isinstance(data, dict) or not data:
            print("  No data available.\n")
            return
        print("  Field                    Value")
        print("  ------------------------- ------------------------------------------------------------")
        for k, v in data.items():
            label = k.replace("_", " ").capitalize()
            print(f"  {label:<25} {v}")
        print()

    print_section("Germline Classification", results.get("germline"))
    print_section("Clinical Impact Classification", results.get("clinical_impact"))
    print_section("Oncogenicity Classification", results.get("oncogenicity"))
