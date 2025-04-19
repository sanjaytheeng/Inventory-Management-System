from django import forms
from dal import autocomplete
from django.db.models import Sum
from .models import InventoryItem, Agent, Assignment

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'description', 'category', 'total_quantity', 'unit_price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['name', 'contact_info', 'contact_number', 'email']
        widgets = {
            'contact_info': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter additional contact information'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Enter contact number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email address'}),
        }

class AssignmentForm(forms.ModelForm):
    agent_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control select2-agent'}),
        label="Agent"
    )

    inventory_item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Inventory Item"
    )

    class Meta:
        model = Assignment
        fields = ['inventory_item', 'agent_name', 'quantity', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        inventory_item = self.cleaned_data.get('inventory_item')

        if not inventory_item:
            raise forms.ValidationError("Please select an inventory item.")

        if quantity > inventory_item.available_quantity:
            raise forms.ValidationError(f"Only {inventory_item.available_quantity} items available.")

        return quantity

    def clean_agent_name(self):
        agent_name = self.cleaned_data.get('agent_name')
        if not agent_name:
            raise forms.ValidationError("Agent name is required.")
        return agent_name

class AssignmentReturnForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['status', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

class InventoryQuantityUpdateForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['total_quantity']

    def save(self, commit=True):
        inventory_item = super().save(commit=False)

        # Recalculate available and in-use counts
        total_assigned = inventory_item.assignments.aggregate(
            total_assigned=Sum('quantity')
        )['total_assigned'] or 0

        inventory_item.available_quantity = inventory_item.total_quantity - total_assigned
        inventory_item.in_use_quantity = total_assigned

        if commit:
            inventory_item.save()

        return inventory_item
