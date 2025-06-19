from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .models import Company
from django.utils.decorators import method_decorator
from .utils import require_permission, log_action, user_has_permission

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

@method_decorator(require_permission('add_company'), name='dispatch')
class CompanyCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = Company
    fields = ['name', 'code', 'address']
    template_name = 'company_form.html'
    success_url = reverse_lazy('company_list')

@method_decorator(require_permission('view_company'), name='dispatch')
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
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib.auth import get_user_model, logout
from django.conf import settings
from .forms import CompanyUserCreationForm
from .models import Role, UserRole, Permission

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
            if target_user.pk == user.pk:
                return True
        return UserRole.objects.filter(user=user, role__name='Admin', company=user.company).exists()

@method_decorator(require_permission('view_company'), name='dispatch')
class CompanyDetailView(LoginRequiredMixin, SuperuserRequiredMixin, DetailView):
    model = Company
    template_name = 'company_detail.html'

@method_decorator(require_permission('change_company'), name='dispatch')
class CompanyUpdateView(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    model = Company
    fields = ['name', 'code', 'address']
    template_name = 'company_form.html'
    success_url = reverse_lazy('company_list')

@method_decorator(require_permission('view_user'), name='dispatch')
class UserListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'user_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_id'])
        context['company'] = company
        context['users'] = User.objects.filter(company=company)
        return context

@method_decorator(require_permission("add_user"), name="dispatch")
class CompanyUserCreateView(View):
    """Create a user within a company with optional role assignment."""

    def get(self, request, company_id):
        company = get_object_or_404(Company, pk=company_id)
        form = CompanyUserCreationForm()
        roles = Role.objects.filter(company=company)
        permissions = Permission.objects.all()
        return render(
            request,
            "user_form.html",
            {"form": form, "roles": roles, "permissions": permissions},
        )

    def post(self, request, company_id):
        company = get_object_or_404(Company, pk=company_id)
        form = CompanyUserCreationForm(request.POST)
        roles = Role.objects.filter(company=company)
        permissions = Permission.objects.all()
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.company = company
            user.save()
            role_id = request.POST.get("role")
            if role_id == "new":
                role_name = request.POST.get("new_role_name")
                role = Role.objects.create(name=role_name, company=company)
                perm_ids = request.POST.getlist("permissions")
                role.permissions.set(Permission.objects.filter(id__in=perm_ids))
            else:
                if role_id:
                    role = get_object_or_404(Role, pk=role_id, company=company)
                else:
                    role = Role.objects.get(name='Admin')
            UserRole.objects.create(user=user, role=role, company=company)
            return redirect("user_list", company_id=company.id)
        return render(
            request,
            "user_form.html",
            {"form": form, "roles": roles, "permissions": permissions},
        )

@method_decorator(require_permission('view_user'), name='dispatch')
class UserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Display details for a user with permission aware actions."""

    model = User
    template_name = 'user_detail.html'
    # Avoid clashing with the request "user" context variable
    context_object_name = 'target'

    def get_context_data(self, **kwargs):
        """Inject permission flags for template button visibility."""
        context = super().get_context_data(**kwargs)
        target = context['target']
        req_user = self.request.user
        context['can_edit'] = user_has_permission(req_user, 'change_user')
        context['can_change_password'] = (
            user_has_permission(req_user, 'user_can_change_password')
            or req_user.pk == target.pk
        )
        context['can_toggle'] = (
            user_has_permission(req_user, 'change_user') and req_user.pk != target.pk
        )
        return context

@method_decorator(require_permission('change_user'), name='dispatch')
class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    template_name = 'user_form.html'

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['require_current'] = self.request.user.pk == self.get_object().pk
        return context

    def form_valid(self, form):
        target = self.get_object()
        if self.request.user.pk == target.pk:
            current = self.request.POST.get('current_password')
            if not target.check_password(current or ''):
                form.add_error(None, 'Current password incorrect')
                return self.form_invalid(form)
        response = super().form_valid(form)
        log_action(self.request.user, 'user_update', target)
        return response

@method_decorator(require_permission('change_user'), name='dispatch')
class UserToggleActiveView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        return redirect('user_detail', pk=pk)


@require_permission('user_can_change_password', allow_self=True)
def change_password_view(request, pk):
    """Allow changing a user's password with permission logic."""
    target = get_object_or_404(User, pk=pk)
    require_current = request.user.pk == target.pk
    if request.method == 'POST':
        current = request.POST.get('current_password')
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        if require_current and not target.check_password(current or ''):
            error = 'Current password incorrect'
        elif p1 and p1 == p2:
            target.set_password(p1)
            target.save()
            log_action(request.user, 'password_change', target)
            return redirect('user_detail', pk=target.pk)
        else:
            error = 'Passwords do not match'
    else:
        error = None
    context = {'target': target, 'error': error, 'require_current': require_current}
    return render(request, 'change_password_form.html', context)

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


class CustomLogoutView(View):
    """Allow GET logout to support navigation link."""

    def get(self, request):
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)

