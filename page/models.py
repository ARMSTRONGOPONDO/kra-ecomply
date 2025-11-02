from django.db import models

class Invoice(models.Model):
    number = models.CharField(max_length=8)
    item = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.number} - {self.item}"
