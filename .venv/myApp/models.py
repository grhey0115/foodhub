from django.db import models

class Transaction(models.Model):
    ubtransact_id = models.IntegerField(primary_key=True)
    order_date = models.DateField()
    desc = models.CharField(max_length=255)
    size = models.CharField(max_length=50)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
