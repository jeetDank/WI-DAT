from django.urls import path
from .views.fetch_cik import fetch_cik
from .views.fetch_sec_filing_url import fetch_latest_filings
from .views.download_sec_filings import download_sec_filings
from .views.fetch_company_news import fetch_news_articles
from .views.extract_financial_data import extract_financial_data

urlpatterns = [
   path('fetch-cik/',fetch_cik),
   path('fetch-sec-filing-url/', fetch_latest_filings),
   path('download-sec-filings/', download_sec_filings),
   path('fetch_news_articles/',fetch_news_articles),
   path('extract_financial_data/',extract_financial_data)
]