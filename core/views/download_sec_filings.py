import os
import json
import requests
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import traceback
from ..constants import USER_AGENT, HEADERS
from django.conf import settings
from rest_framework.decorators import api_view

# Constants (Move these to a separate constants.py file if needed)
USER_AGENT = "Anant Kulkarni-Ideas To Impacts Innovation Pvt. Ltd.-anant.kulkarni@ideastoimpacts.com"
HEADERS = {"User-Agent": USER_AGENT}

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
@api_view(['POST'])
def download_sec_filings(request):
    try:
        data = json.loads(request.body)
        cik_number = data.get("cik")
        filings_json_path = data.get("filings_path")
        user_start_year = int(data.get("start_year"))
        user_end_year = int(data.get("end_year"))

        filings_dir = os.path.join(settings.MEDIA_ROOT, cik_number)
        filing_folder = os.path.join(filings_dir, "filing")
        os.makedirs(filing_folder, exist_ok=True)

        filing_json_location = os.path.join(filings_dir, "sec_filing_json", f"{cik_number}.json")

        # Create the file if it doesn't exist
        if not os.path.exists(filing_json_location):
            with open(filing_json_location, "w") as f:
                json.dump({}, f)
            logger.info(f"Created new JSON file at {filing_json_location}")

        # Load JSON from local file
        with open(filing_json_location, "r") as f:
            filings_data = json.load(f)

        # Extract available years
        filing_dates = filings_data.get("filingDate", [])
        if not filing_dates:
            return JsonResponse({"error": "No filing dates found in the JSON file."}, status=400)

        filing_years = sorted(set(datetime.strptime(date, "%Y-%m-%d").year for date in filing_dates))
        start_year = filing_years[0]
        end_year = filing_years[-1]

        if user_start_year < start_year or user_end_year > end_year or user_start_year > user_end_year:
            return JsonResponse({"error": "Invalid year range"}, status=400)

        filtered_filings = [
            (filings_data["form"][i], filings_data["filingDate"][i], filings_data["accessionNumber"][i].replace("-", ""))
            for i in range(len(filing_dates))
            if user_start_year <= datetime.strptime(filing_dates[i], "%Y-%m-%d").year <= user_end_year
        ]

        download_logs = []

        for form_type, date_filed, accession_number in filtered_filings:
            filing_index_url = f"https://www.sec.gov/Archives/edgar/data/{cik_number}/{accession_number}/index.json"
            logger.info(f"Checking documents for {form_type} on {date_filed}")

            index_response = requests.get(filing_index_url, headers=HEADERS)
            if index_response.status_code != 200:
                logger.warning(f"Failed to fetch index for {accession_number}")
                continue

            index_data = index_response.json()
            documents = index_data.get("directory", {}).get("item", [])

            if not documents:
                logger.warning(f"No documents for {form_type} on {date_filed}")
                continue

            for doc in documents:
                file_name = doc["name"]
                file_extension = os.path.splitext(file_name)[-1]
                file_url = f"https://www.sec.gov/Archives/edgar/data/{cik_number}/{accession_number}/{file_name}"
                local_file_path = os.path.join(filing_folder, f"{form_type}_{date_filed}{file_extension}")

                logger.info(f"Downloading {file_name} from {file_url}")
                file_response = requests.get(file_url, headers=HEADERS)

                if file_response.status_code == 200:
                    with open(local_file_path, "wb") as f:
                        f.write(file_response.content)
                    logger.info(f"Saved to {local_file_path}")
                    download_logs.append({"form": form_type, "date": date_filed, "file": file_name})
                else:
                    logger.error(f"Failed to download {file_url}, status: {file_response.status_code}")

        return JsonResponse({"message": "Filings downloaded", "details": download_logs})

    except Exception as e:
        logger.error(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)
