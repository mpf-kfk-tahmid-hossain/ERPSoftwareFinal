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

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(self.request.user, 'login')
        return response
from django.views.generic import DetailView, UpdateView, ListView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib.auth import get_user_model, logout
from django.conf import settings
from .forms import CompanyUserCreationForm
from .models import Role, UserRole, Permission

User = get_user_model()

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
class UserListView(LoginRequiredMixin, TemplateView):
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
        can_add_role = user_has_permission(request.user, 'add_role')
        permissions = Permission.objects.all() if can_add_role else Permission.objects.none()
        return render(
            request,
            "user_form.html",
            {
                "form": form,
                "roles": roles,
                "permissions": permissions,
                "can_add_role": can_add_role,
            },
        )

    def post(self, request, company_id):
        company = get_object_or_404(Company, pk=company_id)
        form = CompanyUserCreationForm(request.POST)
        roles = Role.objects.filter(company=company)
        can_add_role = user_has_permission(request.user, 'add_role')
        permissions = Permission.objects.all() if can_add_role else Permission.objects.none()
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.company = company
            user.save()
            role_id = request.POST.get("role")
            if role_id == "new":
                if not can_add_role:
                    return HttpResponseForbidden()
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
            {
                "form": form,
                "roles": roles,
                "permissions": permissions,
                "can_add_role": can_add_role,
            },
        )

@method_decorator(require_permission('view_user'), name='dispatch')
class UserDetailView(LoginRequiredMixin, DetailView):
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
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    template_name = 'user_form.html'

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target = self.get_object()
        context['require_current'] = self.request.user.pk == target.pk
        context['roles'] = Role.objects.filter(company=target.company)
        can_add_role = user_has_permission(self.request.user, 'add_role')
        context['permissions'] = Permission.objects.all() if can_add_role else Permission.objects.none()
        context['can_add_role'] = can_add_role
        return context

    def form_valid(self, form):
        target = self.get_object()
        if self.request.user.pk == target.pk:
            current = self.request.POST.get('current_password')
            if not target.check_password(current or ''):
                form.add_error(None, 'Current password incorrect')
                return self.form_invalid(form)
        response = super().form_valid(form)
        company = target.company
        role_id = self.request.POST.get('role')
        can_add_role = user_has_permission(self.request.user, 'add_role')
        if role_id == 'new':
            if not can_add_role:
                return HttpResponseForbidden()
            role_name = self.request.POST.get('new_role_name')
            role = Role.objects.create(name=role_name, company=company)
            perm_ids = self.request.POST.getlist('permissions')
            role.permissions.set(Permission.objects.filter(id__in=perm_ids))
        elif role_id:
            role = get_object_or_404(Role, pk=role_id, company=company)
        else:
            role = None
        if role:
            UserRole.objects.update_or_create(user=target, company=company, defaults={'role': role})
        log_action(self.request.user, 'user_update', target)
        return response

@method_decorator(require_permission('change_user'), name='dispatch')
class UserToggleActiveView(LoginRequiredMixin, View):
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

@method_decorator(require_permission('view_role'), name='dispatch')
class RoleListView(LoginRequiredMixin, TemplateView):
    template_name = 'role_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Role.objects.filter(company=self.request.user.company)
        return context


@method_decorator(require_permission('add_role'), name='dispatch')
class RoleCreateView(LoginRequiredMixin, View):
    def get(self, request):
        permissions = Permission.objects.all()
        return render(request, 'role_form.html', {'permissions': permissions})

    def post(self, request):
        name = request.POST.get('name', '').strip()
        if not name:
            permissions = Permission.objects.all()
            return render(request, 'role_form.html', {'permissions': permissions, 'error': 'Name required'})
        role = Role.objects.create(name=name, description=request.POST.get('description', ''), company=request.user.company)
        perm_ids = request.POST.getlist('permissions')
        role.permissions.set(Permission.objects.filter(id__in=perm_ids))
        return redirect('role_list')


@method_decorator(require_permission('change_role'), name='dispatch')
class RoleUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        role = get_object_or_404(Role, pk=pk, company=request.user.company)
        perms = Permission.objects.all()
        assigned = set(role.permissions.values_list('id', flat=True))
        return render(request, 'role_form.html', {'role': role, 'permissions': perms, 'assigned_ids': assigned})

    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk, company=request.user.company)
        name = request.POST.get('name', '').strip()
        if not name:
            perms = Permission.objects.all()
            assigned = set(int(i) for i in request.POST.getlist('permissions'))
            return render(request, 'role_form.html', {'role': role, 'permissions': perms, 'assigned_ids': assigned, 'error': 'Name required'})
        role.name = name
        role.description = request.POST.get('description', '')
        role.save()
        perm_ids = request.POST.getlist('permissions')
        role.permissions.set(Permission.objects.filter(id__in=perm_ids))
        return redirect('role_list')

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
        log_action(request.user, 'logout')
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)

