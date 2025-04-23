# HGVS Variant Classification Tool

This repository contains the following:

1. 'main.py' : main python script
2. 'README.md' : README file
3. 'requirements.txt' : text file with requirements
4. 'test_main.py' : For unit testing
5. 'environment.yml'  : contains required dependencies
6. 'LICENSE' : Apache license details
7. 'clinvar_vlaidation.log' : log file storage set at max 5MB
8. 'codecov.yaml' : Workflow configuration for automated testing 

---

## Salient features:
This was written in a Pycharm IDE. The system used runs MacOS (MacOS Big Sur Version 11.1). 
Runs with Python 3.11.2, Conda 24.5.0. Other requirements are mentioned in requirements.txt and can be installed from environment.yml.

The main script `main.py` is a command-line tool for validating HGVS variants and retrieving classification data from NCBI ClinVar.  
Further details are provided in the script's docstring.

---

## Features

- Validates HGVS variants via VariantValidator API (RefSeq and Ensembl)
- Queries ClinVar (eSearch and eSummary)
- Extracts Germline, Clinical Impact, and Oncogenicity classifications
- Handles missing gene symbol or ClinVar result scenarios
- Rotating logging to `clinvar_validation.log`
- Structured summary formatting using `output.py`
- Includes test coverage via `pytest` and unit test scripts

---

## Installation

Clone and install as an editable package:

```bash
git clone https://github.com/<your-username>/final_coding_project.git
cd final_coding_project
pip install -e .
```

Or activate your environment:

```bash
conda activate myenv
pip install -e .
```

---

## Usage

Run the command-line interface:

```bash
variant-tool
```

You will be prompted for:
- An HGVS variant (e.g., `NM_000518.5:c.92+1G>A`)
- Genome build (`GRCh38` or `GRCh37`)

---

## Example Output

```
HGVS variant 'NM_000518.5:c.92+1G>A' validated successfully for GRCH38.
Gene Symbol: HBB

Clinical Variant Summary
------------------------------
Gene: HBB
Variant UID: 15436

Germline Classification
  Description: Pathogenic
  Last evaluated: 2025/03/04 00:00
  Review status: criteria provided, multiple submitters, no conflicts
  Fda recognized database: 
  Trait set: [...]

Clinical Impact Classification
  No data available.

Oncogenicity Classification
  No data available.
```

If ClinVar returns no match:
```
No results found for HGVS variant 'NM_000314.4:c.850-2A>G' in ClinVar.
This variant may not be clinically annotated yet.
```

If gene symbol is not available:
```
Gene Symbol: Not available — the variant may be intronic or unrecognized by transcript.
```

---

## Project Structure

```
final_coding_project/
├── variant_tool/
│   ├── __init__.py
│   ├── main.py
│   ├── clinvar.py
│   ├── variant_validator.py
│   ├── output.py
├── tests/
│   ├── test_main.py
│   ├── test_output.py
├── pyproject.toml
├── requirements.txt
├── environment.yml
├── codecov.yaml
├── LICENSE
├── README.md
```

---

## Testing

Run all tests using:

```bash
pytest
```

Tests include:
- Core function validation
- Output formatting
- Edge case handling

---

## License

Apache License 2.0

---

## Maintainer Notes

This project is modular and extensible for clinical annotation pipelines.
The current output formatting may be enhanced in future releases.


