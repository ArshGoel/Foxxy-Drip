from django.db import models
from django.contrib.auth.models import User

class PaymentTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merchant_order_id = models.CharField(max_length=64, unique=True)
    phonepe_order_id = models.CharField(max_length=64, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "PENDING"),
            ("SUCCESS", "SUCCESS"),
            ("FAILED", "FAILED")
        ],
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.merchant_order_id
