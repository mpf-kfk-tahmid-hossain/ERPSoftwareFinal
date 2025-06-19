from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .models import Company

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class CompanyCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = Company
    fields = ['name', 'code', 'address']
    template_name = 'company_form.html'
    success_url = reverse_lazy('company_list')

class CompanyListView(LoginRequiredMixin, SuperuserRequiredMixin, TemplateView):
    template_name = 'company_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Company.objects.all()
        return context

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

class CustomLoginView(LoginView):
    template_name = 'login.html'
from django.views.generic import DetailView, UpdateView, ListView, View
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .forms import CompanyUserCreationForm
from .models import Role, UserRole

User = get_user_model()

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        company_id = self.kwargs.get('company_id')
        if company_id and user.company_id != int(company_id):
            return False
        target_pk = self.kwargs.get('pk')
        if target_pk:
            target_user = get_object_or_404(User, pk=target_pk)
            if target_user.company_id != user.company_id:
                return False
        return UserRole.objects.filter(user=user, role__name='Admin', company=user.company).exists()

class CompanyDetailView(LoginRequiredMixin, SuperuserRequiredMixin, DetailView):
    model = Company
    template_name = 'company_detail.html'

class CompanyUpdateView(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    model = Company
    fields = ['name', 'code', 'address']
    template_name = 'company_form.html'
    success_url = reverse_lazy('company_list')

class UserListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'user_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_id'])
        context['company'] = company
        context['users'] = User.objects.filter(company=company)
        return context

class CompanyUserCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    form_class = CompanyUserCreationForm
    template_name = 'user_form.html'

    def get_success_url(self):
        return reverse_lazy('user_list', kwargs={'company_id': self.kwargs['company_id']})

    def form_valid(self, form):
        company = get_object_or_404(Company, pk=self.kwargs['company_id'])
        user = form.save(commit=False)
        user.company = company
        user.save()
        admin_role = Role.objects.get(name='Admin')
        UserRole.objects.create(user=user, role=admin_role, company=company)
        return redirect(self.get_success_url())

class UserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = User
    template_name = 'user_detail.html'

class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = User
    fields = ['email', 'first_name', 'last_name']
    template_name = 'user_form.html'
    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.kwargs['pk']})

class UserToggleActiveView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        return redirect('user_detail', pk=pk)

class WhoAmIView(LoginRequiredMixin, View):
    def get(self, request):
        roles = list(request.user.userrole_set.values_list('role__name', flat=True))
        company = request.user.company.name if request.user.company else None
        return JsonResponse({'username': request.user.username, 'company': company, 'roles': roles})

class DashboardAPI(LoginRequiredMixin, View):
    def get(self, request):
        company = request.user.company.name if request.user.company else None
        return JsonResponse({'username': request.user.username, 'company': company})

# Custom permission denied handler
from django.http import HttpResponseForbidden
from django.template import loader

def permission_denied_view(request, exception):
    if request.path.startswith('/api/'):
        return JsonResponse({'detail': 'Permission denied'}, status=403)
    template = loader.get_template('403.html')
    return HttpResponseForbidden(template.render({}, request))

