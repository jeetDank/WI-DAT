from django.db import models

class Company(models.Model):
    cik_number = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return f"{self.company_name} ({self.cik_number})"