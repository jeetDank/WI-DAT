from core.models.Company import Company
from django.db import IntegrityError

def add_company_if_not_exists(cik_number: str, company_name: str):
    if Company.objects.filter(cik_number=cik_number).exists():
        raise ValueError(f"CIK number '{cik_number}' already exists.")

    try:
        Company.objects.create(cik_number=cik_number, company_name=company_name)
        return f"Company '{company_name}' added successfully."
    except IntegrityError as e:
        raise ValueError("Failed to insert company due to DB integrity error.") from e