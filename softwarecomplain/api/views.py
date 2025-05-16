from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import Software, Complain
from .forms import ComplainForm, ComplainUpdateForm
import json
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'api/dashboard.html'
    model = Complain
    context_object_name = 'recent_complaints'
    paginate_by = 5

    def get_queryset(self):
        return Complain.objects.all().order_by('-created_at')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics for cards
        total_complaints = Complain.objects.count()
        resolved_complaints = Complain.objects.filter(status='Resolved').count()
        in_progress_complaints = Complain.objects.filter(status='In_Progress').count()
        initiated_complaints = Complain.objects.filter(status='Initiated').count()
        not_resolved = total_complaints - resolved_complaints
        
        # Chart data - complaints by software
        software_data = Complain.objects.values('software__name').annotate(total=Count('id'))
        
        # Chart data - status distribution
        status_data = Complain.objects.values('status').annotate(total=Count('id'))
        
        context.update({
            'total_complaints': total_complaints,
            'resolved_complaints': resolved_complaints,
            'in_progress_complaints': in_progress_complaints,
            'initiated_complaints': initiated_complaints,
            'not_resolved_complaints': not_resolved,
            'software_data': json.dumps(list(software_data)),
            'status_data': json.dumps(list(status_data)),
            'software_list': Software.objects.all(),
        })
        return context

class ComplainListView(LoginRequiredMixin, ListView):
    model = Complain
    template_name = 'api/complain_list.html'
    context_object_name = 'complaints'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtering
        software_filter = self.request.GET.get('software')
        status_filter = self.request.GET.get('status')
        organization_filter = self.request.GET.get('organization')
        
        if software_filter:
            queryset = queryset.filter(software_id=software_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if organization_filter:
            queryset = queryset.filter(organization__icontains=organization_filter)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['software_list'] = Software.objects.all()
        return context

class ComplainDetailView(LoginRequiredMixin, DetailView):
    model = Complain
    template_name = 'api/complain_detail.html'
    context_object_name = 'complain'

class ComplainCreateView(LoginRequiredMixin, CreateView):
    model = Complain
    form_class = ComplainForm
    template_name = 'api/complain_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ComplainUpdateView(LoginRequiredMixin, UpdateView):
    model = Complain
    form_class = ComplainUpdateForm
    template_name = 'api/complain_update.html'
    context_object_name = 'complain'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('complain_detail', kwargs={'pk': self.object.pk})

def analytics_view(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # AJAX request for chart data
        time_period = request.GET.get('period', 'week')
        
        end_date = datetime.now()
        if time_period == 'week':
            start_date = end_date - timedelta(days=7)
        elif time_period == 'month':
            start_date = end_date - timedelta(days=30)
        else:  # year
            start_date = end_date - timedelta(days=365)
        
        # Software distribution data
        software_data = Complain.objects.filter(created_at__range=[start_date, end_date]).values('software__name').annotate(total=Count('id'))
        
        # Status distribution data
        status_data = (
            Complain.objects.filter(created_at__range=[start_date, end_date])
            .values('status')
            .annotate(total=Count('id')))
        
        return JsonResponse({
            'software_data': list(software_data),
            'status_data': list(status_data),
        })
    
    return render(request, 'api/analytics.html')

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Software, Complain
import re

@login_required
@csrf_exempt
@require_POST
def chatbot_response(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request type'}, status=400)
    
    try:
        message = request.POST.get('message', '').strip().lower()
        if not message:
            return JsonResponse({'error': 'Empty message'}, status=400)
        
        # Get user's complaints if they exist
        user_complaints = Complain.objects.filter(created_by=request.user).order_by('-created_at')
        
        # Enhanced response logic with pattern matching
        response = generate_chatbot_response(message, user_complaints)
        
        return JsonResponse({'response': response})
    
    except Exception as e:
        return JsonResponse({
            'error': 'An error occurred',
            'details': str(e)
        }, status=500)

def generate_chatbot_response(message, user_complaints=None):
    # Check for specific patterns
    if re.search(r'\b(hi|hello|hey|greetings)\b', message):
        greeting = "Hello! I'm your Complaint Assistant. How can I help you today?"
        if user_complaints:
            active = user_complaints.filter(status__in=['initiated', 'in_progress']).count()
            if active:
                greeting += f"\n\nYou have {active} active complaint(s)."
        return greeting
    
    elif re.search(r'\b(new|create|submit|report)\b.*\b(complaint|issue|problem)\b', message):
        return ("To create a new complaint:\n"
                "1. Click 'New Complaint' at the top\n"
                "2. Select the software\n"
                "3. Describe your issue\n"
                "4. Submit the form\n\n"
                "Would you like me to open the complaint form for you?")
    
    elif re.search(r'\b(status|progress|update)\b.*\b(complaint|issue)\b', message):
        if user_complaints:
            latest = user_complaints.first()
            if latest:
                return (f"Your most recent complaint (#SC-{latest.id}) about {latest.software.name} "
                       f"is currently {latest.get_status_display()}.\n\n"
                       "For specific complaint status, please provide the complaint ID.")
        return "I can check complaint statuses. Please provide the complaint ID or describe the issue."
    
    elif re.search(r'\b(analytics|stats|statistics|report|metrics)\b', message):
        return ("Complaint analytics available:\n"
                "- By software\n"
                "- By status\n"
                "- By time period\n\n"
                "Visit the Analytics page or ask for specific metrics.")
    
    elif re.search(r'\b(list|show|display)\b.*\b(software|systems?|apps?)\b', message):
        software_list = ", ".join(Software.objects.values_list('name', flat=True))
        return f"Supported software: {software_list}\n\nWhich software are you inquiring about?"
    
    elif re.search(r'\b(help|support|assistance|guide)\b', message):
        return ("I can help with:\n"
                "1. Creating new complaints\n"
                "2. Checking complaint status\n"
                "3. Providing analytics\n"
                "4. Answering process questions\n\n"
                "What would you like help with?")
    
    elif re.search(r'\b(agency|security|charpotra|gov)\b', message):
        return ("You might be looking for:\n"
                "🔗 Local Security Clearance: https://charpotra.gov.bd/agency/\n"
                "🔗 National Security Intelligence: https://www.nsi.gov.bd/\n\n"
                "Is this what you were looking for?")
    
    elif re.search(r'\b(complaint|issue|problem)\b.*\b(id|number|#)\b.*\b(\d+)\b', message):
        # Try to extract complaint ID from message
        match = re.search(r'(\d+)', message)
        if match:
            complaint_id = match.group(1)
            try:
                complaint = Complain.objects.get(id=complaint_id, created_by=request.user)
                return (f"Complaint #SC-{complaint.id}:\n"
                        f"Software: {complaint.software.name}\n"
                        f"Status: {complaint.get_status_display()}\n"
                        f"Created: {complaint.created_at.strftime('%b %d, %Y')}\n\n"
                        f"Description: {complaint.problem_description[:200]}...")
            except Complain.DoesNotExist:
                return f"Complaint #SC-{complaint_id} not found or you don't have access to it."
    
    # Default response
    return ("I'm not sure I understand. Here's what I can help with:\n"
            "- Creating new complaints\n"
            "- Checking complaint status\n"
            "- Providing analytics\n"
            "- Answering process questions\n\n"
            "How can I assist you?")

def download_document(request, pk):
    complain = get_object_or_404(Complain, pk=pk)
    if not complain.attached_document:
        raise Http404("No document attached")
    
    response = FileResponse(complain.attached_document)
    response['Content-Disposition'] = f'attachment; filename="{complain.attached_document.name}"'
    return response