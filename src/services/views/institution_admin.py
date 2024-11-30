from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy
from services.models import Registration, Receipt, Stop, StudentGroup, Ticket, TimeSlot
from services.forms.institution_admin import ReceiptForm, StudentGroupForm, TicketForm

class RegistrationListView(ListView):
    model = Registration
    template_name = 'institution_admin/registration_list.html'
    context_object_name = 'registrations'
    

class TicketListView(ListView):
    model = Ticket
    template_name = 'institution_admin/ticket_list.html'
    context_object_name = 'tickets'
    
    def get_queryset(self):
        # Get registration based on slug
        registration_slug = self.kwargs.get('registration_slug')
        self.registration = get_object_or_404(Registration, slug=registration_slug)
        
        # Base queryset filtered by registration and institution
        queryset = Ticket.objects.filter(registration=self.registration, institution=self.request.user.profile.institution).order_by('-created_at')
        
        # Apply filters based on GET parameters
        pickup_points = self.request.GET.getlist('pickup_point')
        time_slot = self.request.GET.get('time_slot')
        student_group = self.request.GET.get('student_group')
        filters = False  # Default no filters applied

        # Apply filters based on GET parameters and update the filters flag
        if pickup_points and not pickup_points == ['']:
            queryset = queryset.filter(pickup_point_id__in=pickup_points)
            filters = True
        if time_slot:
            queryset = queryset.filter(time_slot_id=time_slot)
            filters = True
        if student_group:
            queryset = queryset.filter(student_group_id=student_group)
            filters = True
        
        # Pass the filters flag to context (done in get_context_data)
        self.filters = filters  # Store in the instance for later access

        return queryset
    
    def get_context_data(self, **kwargs):
        # Get default context from parent
        context = super().get_context_data(**kwargs)
        
        # Add the filter status to the context
        context['filters'] = self.filters  # Pass the filters flag to the template
        
        # Add the filter options to the context
        context['registration'] = self.registration
        context['pickup_points'] = Stop.objects.all()
        context['time_slots'] = TimeSlot.objects.all()
        context['student_groups'] = StudentGroup.objects.all()

        return context


class TicketUpdateView(UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'institution_admin/ticket_update.html'
    slug_url_kwarg = 'ticket_slug'

    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('institution_admin:ticket_list', kwargs={'registration_slug': self.kwargs['registration_slug']})


class ReceiptListView(ListView):
    model = Receipt
    template_name = 'institution_admin/receipt_list.html'
    context_object_name = 'receipts'
    
    
class ReceiptCreateView(CreateView):
    template_name = 'institution_admin/receipt_create.html'
    model = Receipt
    form_class = ReceiptForm
    
    def form_valid(self, form):
        receipt = form.save(commit=False)
        user = self.request.user
        receipt.org = user.profile.org
        receipt.institution = user.profile.institution
        receipt.save()
        return redirect('institution_admin:receipt_list')
    

class ReceiptDeleteView(DeleteView):
    model = Receipt
    template_name = 'institution_admin/receipt_confirm_delete.html'
    slug_url_kwarg = 'receipt_slug'
    success_url = reverse_lazy('institution_admin:receipt_list')
    
    
class StudentGroupListView(ListView):
    model = StudentGroup
    template_name = 'institution_admin/student_group_list.html'
    context_object_name = 'student_groups'  
    
    
class StudentGroupCreateView(CreateView):
    template_name = 'institution_admin/student_group_create.html'
    model = StudentGroup
    form_class = StudentGroupForm
    
    def form_valid(self, form):
        receipt = form.save(commit=False)
        user = self.request.user
        receipt.org = user.profile.org
        receipt.institution = user.profile.institution
        receipt.save()
        return redirect('institution_admin:student_group_list') 
    
    
class StudentGroupUpdateView(UpdateView):
    model = StudentGroup
    form_class = StudentGroupForm
    template_name = 'institution_admin/student_group_update.html'
    slug_url_kwarg = 'student_group_slug'
    success_url = reverse_lazy('institution_admin:student_group_list')

    def form_valid(self, form):
        return super().form_valid(form)
    
    
class StudentGroupDeleteView(DeleteView):
    model = StudentGroup
    template_name = 'institution_admin/student_group_confirm_delete.html'
    slug_url_kwarg = 'student_group_slug'
    success_url = reverse_lazy('institution_admin:student_group_list')
    
    
    