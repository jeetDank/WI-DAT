import os
import json
import pandas as pd
from lxml import etree
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse


def parse_xbrl(file_path):
    tree = etree.parse(file_path)
    root = tree.getroot()

    data = []
    for element in root.iter():
        if element.text and element.text.strip():
            data.append((element.tag, element.text.strip()))

    return data


def process_financial_data(data):
    df = pd.DataFrame(data, columns=["Tag", "Value"])
    keywords = ["Revenue", "Income", "Asset", "Liability", "Cash"]
    df_filtered = df[df["Tag"].str.contains("|".join(keywords), case=False, na=False)]
    return df_filtered


@csrf_exempt
@require_POST
def extract_financial_data(request):
    try:
        body = json.loads(request.body)
        cik_number = body.get("cik_number")
        if not cik_number:
            return JsonResponse({"error": "Missing 'cik_number' in request body"}, status=400)

        filing_folder = os.path.join(settings.MEDIA_ROOT, cik_number, "filing")
        output_folder = os.path.join(settings.MEDIA_ROOT, cik_number, "financial_details")
        os.makedirs(output_folder, exist_ok=True)

        all_data = []
        for filename in os.listdir(filing_folder):
            if filename.endswith(".xml"):
                file_path = os.path.join(filing_folder, filename)
                extracted_data = parse_xbrl(file_path)
                all_data.extend(extracted_data)

        if not all_data:
            return JsonResponse({"message": "No financial data found in XML files."})

        df = process_financial_data(all_data)
        output_file_path = os.path.join(output_folder, "financial_data.csv")
        df.to_csv(output_file_path, index=False)

        relative_path = os.path.relpath(output_file_path, settings.MEDIA_ROOT)
        return JsonResponse({
            "message": "Financial data extracted and saved.",
            "file_path": relative_path
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
