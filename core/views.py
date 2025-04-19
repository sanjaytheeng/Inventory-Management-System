import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .models import InventoryItem, Agent, Assignment, TransactionLog
from .forms import (
    InventoryItemForm, AgentForm, AssignmentForm,
    AssignmentReturnForm, InventoryQuantityUpdateForm
)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from authentication.models import UserActivity
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.timezone import now
from dal import autocomplete
from django.db import transaction
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def home(request):
    inventory_items = InventoryItem.objects.all()
    assignments = Assignment.objects.filter(status='assigned')[:5]
    returned_assignments = Assignment.objects.filter(status='returned')[:5]

    # Calculate assignment status counts
    assignment_status_counts = {
        'assigned': Assignment.objects.filter(status='assigned').count(),
        'returned': Assignment.objects.filter(status='returned').count(),
        'lost': Assignment.objects.filter(status='lost').count(),
        'damaged': Assignment.objects.filter(status='damaged').count(),
    }

    return render(request, 'core/home.html', {
        'inventory_items': inventory_items,
        'assignments': assignments,
        'returned_assignments': returned_assignments,
        'assignment_status_counts': assignment_status_counts,
    })

# Inventory Views
@method_decorator(login_required, name='dispatch')
class InventoryListView(ListView):
    model = InventoryItem
    template_name = 'core/inventory_list.html'
    context_object_name = 'inventory_items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InventoryItemForm()
        return context

@method_decorator(login_required, name='dispatch')
class InventoryDetailView(DetailView):
    model = InventoryItem
    template_name = 'core/inventory_detail.html'
    context_object_name = 'object'

@method_decorator(login_required, name='dispatch')
class InventoryCreateView(CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'core/inventory_form.html'
    success_url = reverse_lazy('core:inventory_list')

    def form_valid(self, form):
        response = super().form_valid(form)

        try:
            # Log the transaction
            TransactionLog.objects.create(
                action='inventory_update',
                user=self.request.user,
                remarks=f"Inventory item {self.object.id} created by {self.request.user.username}"
            )
            logger.info(f"Transaction log created for inventory creation: {self.object.id}")
        except Exception as e:
            logger.error(f"Failed to create transaction log for inventory creation: {e}")

        messages.success(self.request, 'Inventory item created successfully!')
        return response

@method_decorator(login_required, name='dispatch')
class InventoryUpdateView(UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'core/inventory_form.html'
    success_url = reverse_lazy('core:inventory_list')

    def get_form_class(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return InventoryQuantityUpdateForm
        return self.form_class

    def form_valid(self, form):
        response = super().form_valid(form)

        try:
            # Log the transaction
            TransactionLog.objects.create(
                action='inventory_update',
                user=self.request.user,
                remarks=f"Inventory item {self.object.id} updated by {self.request.user.username}"
            )
        except Exception as e:
            logger.error(f"Failed to create transaction log for inventory update: {e}")

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Handle AJAX request for quantity update
            return JsonResponse({
                'success': True,
                'message': 'Quantity updated successfully!',
                'total_quantity': form.instance.total_quantity,
                'available_quantity': form.instance.available_quantity,
                'in_use_quantity': form.instance.in_use_quantity
            })
        else:
            # Handle regular form submission
            messages.success(self.request, 'Inventory item updated successfully!')
            return response

@method_decorator(login_required, name='dispatch')
class InventoryDeleteView(DeleteView):
    model = InventoryItem
    template_name = 'core/inventory_confirm_delete.html'
    success_url = reverse_lazy('core:inventory_list')

    def delete(self, request, *args, **kwargs):
        object = self.get_object()

        try:
            # Log the transaction
            TransactionLog.objects.create(
                action=f'{self.model.__name__.lower()}_delete',
                user=request.user,
                remarks=f"{self.model.__name__} {object.id} deleted by {request.user.username}"
            )
        except Exception as e:
            logger.error(f"Failed to create transaction log for {self.model.__name__.lower()} deletion: {e}")

        messages.success(request, f'{self.model.__name__} deleted successfully!')
        return super().delete(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class InventoryQuantityUpdateView(UpdateView):
    model = InventoryItem
    form_class = InventoryQuantityUpdateForm
    template_name = 'core/inventory_quantity_update.html'
    success_url = reverse_lazy('core:inventory_list')

    def form_valid(self, form):
        messages.success(self.request, 'Inventory quantity updated successfully!')
        return super().form_valid(form)

# Assignment Views
@method_decorator(login_required, name='dispatch')
class AssignmentListView(ListView):
    model = Assignment
    template_name = 'core/assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        return Assignment.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AssignmentForm()
        context['inventory_items'] = InventoryItem.objects.all()  # Add inventory items to context
        return context

@method_decorator(login_required, name='dispatch')
class AssignmentDetailView(DetailView):
    model = Assignment
    template_name = 'core/assignment_detail.html'
    context_object_name = 'object'

@method_decorator(login_required, name='dispatch')
class AssignmentCreateView(CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'core/assignment_form.html'
    success_url = reverse_lazy('core:assignment_list')

    def form_valid(self, form):
        agent_name = form.cleaned_data['agent_name']
        
        # Try to get existing agent, or create new one with origin
        agent, created = Agent.objects.get_or_create(
            name=agent_name,
            defaults={
                'record_origin': 'assignment_form'  # Indicates agent was created from assignment
            }
        )
        
        # Set the agent for the assignment
        form.instance.agent = agent
        form.instance.agent_name = agent_name
        
        # Save the assignment
        self.object = form.save()

        # Log the transaction
        TransactionLog.objects.create(
            action='assignment_create',
            user=self.request.user,
            remarks=f"Assignment {self.object.id} created for agent {agent_name} {'(new agent created)' if created else '(existing agent)'}"
        )

        # Check if request is AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Assignment created successfully!' + (' New agent was created.' if created else ''),
                'assignment': {
                    'id': self.object.id,
                    'inventory_item': self.object.inventory_item.name,
                    'agent_name': self.object.agent_name,
                    'quantity': self.object.quantity,
                    'assigned_date': self.object.assigned_date.strftime('%b %d, %Y'),
                    'status': self.object.get_status_display(),
                }
            })
        
        messages.success(
            self.request, 
            'Assignment created successfully!' + (' New agent was created.' if created else '')
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class AssignmentUpdateView(UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'core/assignment_form.html'
    success_url = reverse_lazy('core:assignment_list')

    def dispatch(self, request, *args, **kwargs):
        assignment = self.get_object()
        if assignment.status == 'returned':
            messages.error(request, "You cannot edit an assignment that has been marked as returned.")
            return redirect('core:assignment_list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True  # Add a flag to indicate update mode
        return context

    def form_valid(self, form):
        agent_name = form.cleaned_data['agent_name']
        agent, created = Agent.objects.get_or_create(
            name=agent_name,
            defaults={'record_origin': 'manual'}
        )

        # Ensure only one agent is associated
        if not created:
            agent = Agent.objects.filter(name=agent_name).first()

        form.instance.agent = agent
        response = super().form_valid(form)

        TransactionLog.objects.create(
            action='assignment_update',
            user=self.request.user,
            remarks=f"Assignment {self.object.id} updated for agent {agent_name}"
        )
        messages.success(self.request, 'Assignment updated successfully!')
        return response

@login_required
def assignment_return(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        form = AssignmentReturnForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment.status = 'returned'
            assignment.save()

            # Log the transaction
            TransactionLog.objects.create(
                action='assignment_action',
                user=request.user,
                remarks=f"Assignment {assignment.id} returned by {request.user.username}"
            )

            messages.success(request, 'Item returned successfully!')
            return redirect('core:assignment_list')
    else:
        form = AssignmentReturnForm(instance=assignment)
    return render(request, 'core/assignment_return.html', {
        'form': form,
        'assignment': assignment
    })

@login_required
def mark_assignment_as_returned(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if assignment.status == 'returned':
        messages.warning(request, "This assignment is already marked as returned.")
        return redirect('core:assignment_list')

    try:
        with transaction.atomic():
            # Mark assignment as returned
            assignment.status = 'returned'
            assignment.return_date = now()
            assignment.save()

            # Log the transaction
            TransactionLog.objects.create(
                action='assignment_action',
                user=request.user,
                remarks=f"Assignment {assignment.id} marked as returned by {request.user.username}"
            )

        messages.success(request, "Assignment marked as returned successfully.")
    except ValidationError as e:
        messages.error(request, f"Error: {e.message}")

    return redirect('core:assignment_list')

@method_decorator(login_required, name='dispatch')
class AssignmentDeleteView(DeleteView):
    model = Assignment
    template_name = 'core/assignment_confirm_delete.html'
    success_url = reverse_lazy('core:assignment_list')

    def delete(self, request, *args, **kwargs):
        object = self.get_object()

        try:
            # Log the transaction
            TransactionLog.objects.create(
                action=f'{self.model.__name__.lower()}_delete',
                user=request.user,
                remarks=f"{self.model.__name__} {object.id} deleted by {request.user.username}"
            )
            logger.info(f"Transaction log created for {self.model.__name__.lower()} deletion: {object.id}")
        except Exception as e:
            logger.error(f"Failed to create transaction log for {self.model.__name__.lower()} deletion: {e}")

        messages.success(request, f'{self.model.__name__} deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
# Agent Views
@method_decorator(login_required, name='dispatch')
class AgentListView(ListView):
    model = Agent
    template_name = 'core/agent_list.html'
    context_object_name = 'agents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AgentForm()
        return context

@method_decorator(login_required, name='dispatch')
class AgentDetailView(DetailView):
    model = Agent
    template_name = 'core/agent_detail.html'
    context_object_name = 'object'

@method_decorator(login_required, name='dispatch')
class AgentCreateView(CreateView):
    model = Agent
    form_class = AgentForm
    template_name = 'core/agent_form.html'
    success_url = reverse_lazy('core:agent_list')

    def form_valid(self, form):
        # Set the record origin for agents created through the agent form
        form.instance.record_origin = 'manual'
        
        # Check for existing agent with the same details
        existing_agent = Agent.objects.filter(
            name=form.cleaned_data['name'],
            contact_info=form.cleaned_data['contact_info'],
            contact_number=form.cleaned_data['contact_number'],
            email=form.cleaned_data['email']
        ).first()

        if existing_agent:
            messages.error(self.request, 'An agent with these details already exists.')
            return self.form_invalid(form)

        response = super().form_valid(form)

        # Log the transaction
        TransactionLog.objects.create(
            action='agent_action',
            user=self.request.user,
            remarks=f"Agent {self.object.id} created by {self.request.user.username}"
        )

        messages.success(self.request, 'Agent created successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class AgentUpdateView(UpdateView):
    model = Agent
    form_class = AgentForm
    template_name = 'core/agent_form.html'
    success_url = reverse_lazy('core:agent_list')

    def form_valid(self, form):
        response = super().form_valid(form)

        try:
            # Log the transaction
            TransactionLog.objects.create(
                action='agent_action',
                user=self.request.user,
                remarks=f"Agent {self.object.id} updated by {self.request.user.username}"
            )
        except Exception as e:
            logger.error(f"Failed to create transaction log for agent update: {e}")

        messages.success(self.request, 'Agent updated successfully!')
        return response

@method_decorator(login_required, name='dispatch')
class AgentDeleteView(DeleteView):
    model = Agent
    template_name = 'core/agent_confirm_delete.html'
    success_url = reverse_lazy('core:agent_list')

    def delete(self, request, *args, **kwargs):
        object = self.get_object()

        try:
            # Log the transaction
            TransactionLog.objects.create(
                action=f'{self.model.__name__.lower()}_delete',
                user=request.user,
                remarks=f"{self.model.__name__} {object.id} deleted by {request.user.username}"
            )
        except Exception as e:
            logger.error(f"Failed to create transaction log for {self.model.__name__.lower()} deletion: {e}")

        messages.success(request, f'{self.model.__name__} deleted successfully!')
        return super().delete(request, *args, **kwargs)

# API Views for Autocomplete
class AgentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Agent.objects.none()
        
        qs = Agent.objects.all().order_by('name')
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def get_results(self, context):
        results = []
        for agent in context['object_list']:
            contact_info = agent.contact_number if agent.contact_number else 'No contact'
            name = agent.name.strip()
            results.append({
                'id': name,
                'text': f"{name} ({contact_info})",
                'selected_text': name  # This will be used when the option is selected
            })
        return results

class InventoryItemAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return InventoryItem.objects.none()
        qs = InventoryItem.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def get_results(self, context):
        results = []
        for item in context['object_list']:
            results.append({
                'id': item.pk,
                'text': f"{item.name} ({item.category})"
            })
        return results

@login_required
def get_available_quantity(request, pk):
    inventory_item = get_object_or_404(InventoryItem, pk=pk)
    return JsonResponse({
        'available_quantity': inventory_item.available_quantity
    })

@csrf_exempt
def validate_agent_name(request):
    if request.method == "POST":
        agent_name = request.POST.get("agent_name", "").strip()
        if not agent_name:
            return JsonResponse({"error": "Agent name is required."}, status=400)

        existing_agents = Agent.objects.filter(name__iexact=agent_name)
        if existing_agents.exists():
            return JsonResponse({"exists": True})
        
        return JsonResponse({"is_new": True})

    return JsonResponse({"error": "Invalid request method."}, status=405)

@method_decorator(login_required, name='dispatch')
class TransactionLogListView(ListView):
    model = TransactionLog
    template_name = 'core/transaction_logs.html'
    context_object_name = 'transaction_logs'
    paginate_by = 10

    def get_queryset(self):
        return TransactionLog.objects.order_by('-date_time')
