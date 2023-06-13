ZENODO_BASE = 'https://zenodo.org/'
ZENODO_BASE_RECORD = 'https://zenodo.org/record/'

AVAILABLE_DATASET_RECORDS = {
    'prospect': '6602020',
    'prospectptm_multi_ptm': '7998644',
    'prospectptm_tmt': '8003138',
    'prospectptm_tmt_ptm': '8003152',
    'prospectptm_test_ptm': '8003156'
}

AVAILABLE_DATASET_URLS = {k: ZENODO_BASE_RECORD + v for k, v in AVAILABLE_DATASET_RECORDS.items()}