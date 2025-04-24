from django.conf import settings
import os
import json

def save_filing_json(cik_number, data):
    # Save to MEDIA_ROOT/filings/
    filings_dir = os.path.join(settings.MEDIA_ROOT, cik_number)
    os.makedirs(filings_dir, exist_ok=True)
    os.makedirs(f'{filings_dir}/filing', exist_ok=True)
    os.makedirs(f'{filings_dir}/news', exist_ok=True)
    os.makedirs(f'{filings_dir}/finacialData', exist_ok=True)
    os.makedirs(f'{filings_dir}/sec_filing_json', exist_ok=True)

    file_path = os.path.join(f'{filings_dir}/sec_filing_json/', f"{cik_number}.json")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

    return f"{settings.MEDIA_URL}{cik_number}/sec_filing_json/{cik_number}.json"