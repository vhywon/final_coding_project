import requests
import json


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
    # Validate input
    if not isinstance(hgvs_variant, str) or not hgvs_variant.strip():
        raise ValueError("HGVS variant must be a non-empty string")

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'clinvar',
        'term': f'"{hgvs_variant.strip()}"[hgvs]',  # Search for exact HGVS match
        'retmode': 'json',
        'retmax': 1,  # Limit to 1 result
        'usehistory': 'y'  # Enable history for fetching details
    }

    try:
        # Search for ClinVar IDs
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        search_data = response.json()

        # Check if there are any results
        if 'esearchresult' not in search_data or int(search_data['esearchresult']['count']) == 0:
            return None

        # Fetch detailed records using esummary
        webenv = search_data['esearchresult']['webenv']
        query_key = search_data['esearchresult']['querykey']

        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {
            'db': 'clinvar',
            'query_key': query_key,
            'WebEnv': webenv,
            'retmode': 'json',
            'retmax': 1  # Limit to 1 result
        }

        summary_response = requests.get(summary_url, params=summary_params, timeout=10)
        summary_response.raise_for_status()
        summary_data = summary_response.json()

        return summary_data if 'result' in summary_data else None

    except requests.exceptions.Timeout:
        print(f"Request timed out after 10 seconds for HGVS variant: {hgvs_variant}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error during ClinVar API request for HGVS variant '{hgvs_variant}': {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response for HGVS variant '{hgvs_variant}': {e}")
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
    # Extract fields
    clinical_significance = result_data.get('clinical_significance', {})
    germline_classification = result_data.get('germline_classification', 'No germline classification available')
    clinical_impact = result_data.get('clinical_impact_classification', 'No clinical impact classification available')
    oncogenicity_classification = result_data.get('oncogenicity_classification', 'No oncogenicity classification available')

    return {
        'uid': uid,
        'clinical_significance': clinical_significance,
        'germline_classification': germline_classification,
        'clinical_impact_classification': clinical_impact,
        'oncogenicity_classification': oncogenicity_classification
    }


def main():
    """Main function to execute the ClinVar API search and display specific classifications."""
    try:
        hgvs_variant = input("Enter the HGVS variant to search ClinVar (e.g., NM_000518.5:c.92+1G>A): ").strip()
        clinvar_results = search_clinvar_by_hgvs(hgvs_variant)

        if clinvar_results and 'result' in clinvar_results and clinvar_results['result'] and 'uids' in clinvar_results[
            'result']:
            # Extract the first (and only) result's UID and its data
            result_uid = clinvar_results['result']['uids'][0]  # Directly access the first UID
            result_data = clinvar_results['result'].get(result_uid, {})

            # Extract and display classifications
            classifications = extract_classifications(result_data, result_uid)

            print(f"\nClinVar Results for HGVS variant '{hgvs_variant}' (UID: {classifications['uid']}):")
            print(f"Germline Classification: {classifications['germline_classification']}")
            print(f"Clinical Impact Classification: {classifications['clinical_impact_classification']}")
            print(f"Oncogenicity Classification: {classifications['oncogenicity_classification']}")
        else:
            print(f"No results found for HGVS variant '{hgvs_variant}' in ClinVar.")

    except ValueError as e:
        print(f"Input error: {e}")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
