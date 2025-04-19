from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.conf import settings

class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('furniture', 'Furniture'),
        ('electronics', 'Electronics'),
        ('appliances', 'Appliances'),
        ('tools', 'Tools'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True, null=True, help_text="Optional category for classification")
    total_quantity = models.PositiveIntegerField(default=0, help_text="Total quantity of items")
    in_use_quantity = models.PositiveIntegerField(default=0, help_text="Quantity currently in use")
    available_quantity = models.PositiveIntegerField(default=0, help_text="Quantity available for assignment")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

    def save(self, *args, **kwargs):
        self.available_quantity = self.total_quantity - self.in_use_quantity
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        ordering = ['-created_at']

class Agent(models.Model):
    ORIGIN_CHOICES = [
        ('manual', 'Manual Entry'),
        ('assignment_form', 'Created from Assignment'),
    ]
    
    name = models.CharField(max_length=100)
    contact_info = models.TextField(blank=True, help_text="Additional contact information")
    contact_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    record_origin = models.CharField(
        max_length=50, 
        choices=ORIGIN_CHOICES,
        default='manual',
        help_text="Indicates how the agent record was created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class Assignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('returned', 'Returned'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]

    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='assignments')
    agent_name = models.CharField(max_length=100, help_text="Free-text field for agent's name")
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, help_text="Optional reference to an existing agent record")
    quantity = models.PositiveIntegerField()
    assigned_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.inventory_item.name} - {self.agent_name} ({self.quantity})"

    def save(self, *args, **kwargs):
        if not self.pk:  # New assignment
            self.inventory_item.in_use_quantity += self.quantity
        else:  # Updating an existing assignment
            original = Assignment.objects.get(pk=self.pk)
            quantity_difference = self.quantity - original.quantity

            if self.status == 'returned':
                if self.inventory_item.in_use_quantity < original.quantity:
                    raise ValidationError("Cannot return more items than are currently in use.")
                self.inventory_item.in_use_quantity -= original.quantity
                self.inventory_item.available_quantity += original.quantity
            elif self.status in ['lost', 'damaged']:
                if original.status == 'returned':
                    self.inventory_item.in_use_quantity += original.quantity
                    self.inventory_item.available_quantity -= original.quantity
            else:
                self.inventory_item.in_use_quantity += quantity_difference

        self.inventory_item.available_quantity = self.inventory_item.total_quantity - self.inventory_item.in_use_quantity
        self.inventory_item.save()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.inventory_item.in_use_quantity -= self.quantity
        self.inventory_item.available_quantity = self.inventory_item.total_quantity - self.inventory_item.in_use_quantity
        self.inventory_item.save()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class TransactionLog(models.Model):
    ACTION_CHOICES = [
        ('inventory_update', 'Inventory Update'),
        ('assignment_action', 'Assignment Action'),
    ]

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=now)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.action} by {self.user.username} on {self.date_time}"
