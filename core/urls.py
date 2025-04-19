from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .views import TransactionLogListView

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('inventory/', views.InventoryListView.as_view(), name='inventory_list'),
    path('inventory/add/', views.InventoryCreateView.as_view(), name='inventory_create'),
    path('inventory/<int:pk>/', views.InventoryDetailView.as_view(), name='inventory_detail'),
    path('inventory/<int:pk>/edit/', views.InventoryUpdateView.as_view(), name='inventory_update'),
    path('inventory/<int:pk>/delete/', views.InventoryDeleteView.as_view(), name='inventory_delete'),
    path('inventory/<int:pk>/available/', views.get_available_quantity, name='inventory_available'),
    path('inventory/<int:pk>/update-quantity/', views.InventoryQuantityUpdateView.as_view(), name='inventory_quantity_update'),
    
    path('assignments/', views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignments/add/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    # path('assignments/<int:pk>/edit/', views.AssignmentUpdateView.as_view(), name='assignment_update'),
    path('assignments/<int:pk>/return/', views.assignment_return, name='assignment_return'),
    path('assignments/<int:pk>/delete/', views.AssignmentDeleteView.as_view(), name='assignment_delete'),
    path('assignments/<int:pk>/return/', views.mark_assignment_as_returned, name='assignment_return'),
    
    path('agents/', views.AgentListView.as_view(), name='agent_list'),
    path('agents/add/', views.AgentCreateView.as_view(), name='agent_create'),
    path('agents/<int:pk>/', views.AgentDetailView.as_view(), name='agent_detail'),
    path('agents/<int:pk>/edit/', views.AgentUpdateView.as_view(), name='agent_update'),
    path('agents/<int:pk>/delete/', views.AgentDeleteView.as_view(), name='agent_delete'),

    path('agent-autocomplete/', views.AgentAutocomplete.as_view(), name='agent-autocomplete'),
    path('inventoryitem-autocomplete/', views.InventoryItemAutocomplete.as_view(), name='inventoryitem-autocomplete'),
    path('transaction-logs/', TransactionLogListView.as_view(), name='transaction_logs'),
    path('validate-agent-name/', views.validate_agent_name, name='validate-agent-name'),
]
