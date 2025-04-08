# final_coding_project
This repository contains the files of the final coding project for Unit-III of PGCert Clinical bioinformatics.
Project Description:
The goal of this project is to develop a Python script that allows users to input an HGVS variant,
 which is then passed to the ClinVar API to retrieve relevant clinical information. 
ClinVar is a public NCBI database that provides insights into the clinical significance of genetic variants. 
The API enables access to detailed data about these variants, which is returned in JSON format.
Features:
HGVS Variant Input: The user will input a variant in the HGVS format.
ClinVar API Integration: The variant is sent to the ClinVar API to fetch clinical data.
Data Parsing: The output, returned as a JSON file, will be parsed to extract specific fields, including:
Gene-level classification
Clinical significance
Oncogenic classification
Variant Validation: Before sending the variant to ClinVar, it will be validated using the VariantValidator (VV) to ensure it is properly formatted.
This project aims to provide an easy-to-use tool for accessing critical clinical information related to genetic variants.
