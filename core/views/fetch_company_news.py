import os
import csv
import json
import logging
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from ..constants import GOOGLE_NEWS_API_KEY

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def fetch_news_articles(request):
    try:
        data = json.loads(request.body)
        search_query = data.get("query", "").strip()
        cik_number = data.get("cik_number","").strip()

        if not search_query:
            return JsonResponse({"error": "Search query is required."}, status=400)

        # Build API URL
        news_api_url = (
            f"https://newsapi.org/v2/everything?"
            f"q={search_query}&sortBy=publishedAt&apiKey={GOOGLE_NEWS_API_KEY}"
        )

        logger.info(f"Fetching news for query: {search_query}")
        response = requests.get(news_api_url)

        if response.status_code != 200:
            return JsonResponse({"error": f"Failed to fetch news. Status: {response.status_code}"}, status=500)

        news_data = response.json()
        articles = news_data.get("articles", [])

        results = []
        for i, article in enumerate(articles[:10]):  # Limit to 10
            results.append({
                "title": article["title"],
                "publishedAt": article["publishedAt"],
                "source": article["source"]["name"],
                "url": article["url"]
            })

        # Save results to CSV
        csv_folder = f"{settings.MEDIA_ROOT}{cik_number}/news/"
        print(csv_folder)
        os.makedirs(csv_folder, exist_ok=True)
        csv_filename = os.path.join(csv_folder, f"{search_query.replace(' ', '_')}_news.csv")
        print(csv_filename)
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Published Date", "Source", "URL"])
            for article in results:
                writer.writerow([
                    article["title"],
                    article["publishedAt"],
                    article["source"],
                    article["url"]
                ])

        return JsonResponse({"message": "Articles fetched successfully", "articles": results, "csv_file": csv_filename})

    except Exception as e:
        logger.error(str(e))
        return JsonResponse({"error": "Something went wrong", "details": str(e)}, status=500)
