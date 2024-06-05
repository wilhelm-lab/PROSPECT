ZENODO_BASE = "https://zenodo.org/"
ZENODO_BASE_RECORD = "https://zenodo.org/record/"

AVAILABLE_DATASET_RECORDS = {
    "prospect": "6602020",
    "tmt": "8221499",
    "multi_ptm": "11472525",
    "tmt_ptm": "11474099",
    "test_ptm": "11477731",
}

AVAILABLE_DATASET_URLS = {
    k: ZENODO_BASE_RECORD + v for k, v in AVAILABLE_DATASET_RECORDS.items()
}
