
import fe
from  ..constants import BROWSE_EDGAR_URL,STATUS_FAILURE,STATUS_SUCCESS,HEADERS
import json
from django.views.decorators.csrf import csrf_exempt
import requests
import re
from django.http import JsonResponse
from ..tasks.add_company_in_db import add_company_if_not_exists


@csrf_exempt
def fetch_cik(request):
    """Fetches the CIK number for a given company name from SEC."""
    # company_name = request.POST.get.company_name

    body = json.loads(request.body)
    company_name = body.get("company_name")
    search_url = BROWSE_EDGAR_URL.format(company_name.replace(' ', '+'))
    print(f"Fetching CIK for: {company_name}...")

    response = requests.get(search_url, headers=HEADERS)
    if response.status_code == 200:
        cik_match = re.search(r"CIK=(\d+)", response.text)
        if cik_match:
            cik_number = cik_match.group(1).strip()
            try:
                msg = add_company_if_not_exists(cik_number,company_name)
                return JsonResponse(
                    {"status": STATUS_SUCCESS, "data": {"cik_number": cik_number, "company_name": company_name}},
                    safe=False)
            except Exception as e:
                return JsonResponse({"status": STATUS_FAILURE, "error":str(e) }, safe=False)


    print("⚠ CIK not found on SEC page. Trying alternate lookup...")
    return JsonResponse({"status": STATUS_FAILURE, "data":{} }, safe=False)