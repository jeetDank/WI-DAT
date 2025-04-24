from django.http import JsonResponse
from ..constants import STATUS_FAILURE,SUBMISSIONS_URL,HEADERS,STATUS_SUCCESS
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from ..tasks.save_filings_json import save_filing_json
from ..tasks.add_company_in_db import add_company_if_not_exists


@csrf_exempt
def fetch_latest_filings(request):
    """Fetches the latest SEC filings for a given CIK number."""

    body = json.loads(request.body)
    print(body)
    cik_number = body.get("cik_number")


    if not cik_number:
        return JsonResponse({"status":STATUS_FAILURE,"msg":"Invalid CIK Number",data:[]})

    cik_padded = cik_number.zfill(10)
    filings_url = SUBMISSIONS_URL.format(cik_padded)

    print(f"\nFetching latest SEC filings for CIK {cik_padded}...")
    response = requests.get(filings_url, headers=HEADERS)

    if response.status_code == 200:
        try:
            filings_data = response.json()
            if "filings" not in filings_data:
                return JsonResponse({"status":STATUS_FAILURE,"msg":f"⚠ No 'filings' key found. Available keys: {list(filings_data.keys())}",data:[]})

            latest_filings = filings_data["filings"].get("recent", [])
            if not latest_filings:
                return JsonResponse({"status":STATUS_FAILURE,"msg":"⚠ No recent filings found in 'filings' section.",data:[]})



            file_path = save_filing_json(cik_number,latest_filings)

            return JsonResponse({"status": STATUS_SUCCESS,
                                 "msg": "Filings Found" ,
                                 "data": file_path})



        except (json.JSONDecodeError, TypeError) as e:
            print(f"⚠ Error decoding JSON from SEC response: {e}")
    else:
        print(f"❌ HTTP Error {response.status_code}: Unable to fetch filings.")

