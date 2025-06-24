from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .models import Company
import json
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from .utils import (
    require_permission,
    log_action,
    user_has_permission,
    AdvancedListMixin,
)

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

@method_decorator(require_permission('add_company'), name='dispatch')
class CompanyCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = Company
    fields = ['name', 'address']
    template_name = 'company_form.html'
    success_url = reverse_lazy('company_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get('form')
        context['name'] = (form['name'].value() or '') if form else ''
        context['address'] = (form['address'].value() or '') if form else ''
        return context

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['name'] = form.data.get('name', '')
        context['address'] = form.data.get('address', '')
        return self.render_to_response(context)

    def form_valid(self, form):
        form.instance.code = Company._generate_code()
        return super().form_valid(form)

@method_decorator(require_permission('view_company'), name='dispatch')
class CompanyListView(LoginRequiredMixin, SuperuserRequiredMixin, AdvancedListMixin, TemplateView):
    template_name = 'company_list.html'
    model = Company
    search_fields = ['name', 'code', 'address']
    default_sort = 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = True
        context['filters'] = []
        context['sort_options'] = [
            ('name', 'Name'),
            ('code', 'Code'),
            ('address', 'Address'),
        ]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        context['can_add_user'] = user_has_permission(self.request.user, 'add_user')
        return context

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            self.request.user,
            'login',
            request_type=self.request.method,
            company=self.request.user.company,
        )
        return response
from django.views.generic import DetailView, UpdateView, ListView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib.auth import get_user_model, logout
from django.conf import settings
from .forms import CompanyUserCreationForm
from .models import Role, UserRole, Permission, AuditLog

User = get_user_model()

@method_decorator(require_permission('view_company'), name='dispatch')
class CompanyDetailView(LoginRequiredMixin, SuperuserRequiredMixin, DetailView):
    model = Company
    template_name = 'company_detail.html'

@method_decorator(require_permission('change_company'), name='dispatch')
class CompanyUpdateView(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    model = Company
    fields = ['name', 'address']
    template_name = 'company_form.html'
    success_url = reverse_lazy('company_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        context['company'] = company
        context['name'] = company.name
        context['address'] = company.address
        return context

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['name'] = form.data.get('name', '')
        context['address'] = form.data.get('address', '')
        return self.render_to_response(context)



@method_decorator(require_permission('view_user'), name='dispatch')
class UserListView(LoginRequiredMixin, AdvancedListMixin, TemplateView):
    template_name = 'user_list.html'
    model = User
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filter_fields = ['is_active']
    default_sort = 'username'
    paginate_by = 10

    def base_queryset(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_id'])
        self.company = company
        return User.objects.filter(company=company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['company'] = self.company
        context['page_obj'] = page
        context['search'] = True
        context['sort_options'] = [
            ('username', 'Username'),
            ('email', 'Email'),
            ('is_active', 'Active'),
        ]
        context['filters'] = [
            {
                'name': 'is_active',
                'label': 'Status',
                'current': self.request.GET.get('is_active', ''),
                'options': [
                    {'val': '', 'label': 'All'},
                    {'val': 'True', 'label': 'Active'},
                    {'val': 'False', 'label': 'Inactive'},
                ],
            }
        ]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
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
        context = {
            'form': form,
            'roles': roles,
            'permissions': permissions,
            'can_add_role': can_add_role,
            'username': '',
            'email': '',
            'first_name': '',
            'last_name': '',
        }
        return render(request, "user_form.html", context)

    def post(self, request, company_id):
        company = get_object_or_404(Company, pk=company_id)
        form = CompanyUserCreationForm(request.POST, request.FILES)
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
        context = {
            'form': form,
            'roles': roles,
            'permissions': permissions,
            'can_add_role': can_add_role,
            'username': request.POST.get('username', ''),
            'email': request.POST.get('email', ''),
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
        }
        return render(request, "user_form.html", context)

@method_decorator(require_permission('view_user'), name='dispatch')
class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user_detail.html'
    # Avoid clashing with the request "user" context variable
    context_object_name = 'target'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_superuser and obj.company != self.request.user.company:
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        """Inject permission flags for template button visibility."""
        context = super().get_context_data(**kwargs)
        target = context['target']
        viewer = self.request.user
        context['can_edit'] = user_has_permission(viewer, 'change_user')
        context['can_change_password'] = (
            user_has_permission(viewer, 'user_can_change_password')
            or viewer.pk == target.pk
        )
        context['can_toggle'] = (
            user_has_permission(viewer, 'change_user') and viewer.pk != target.pk
        )
        if user_has_permission(viewer, 'view_role'):
            context['roles'] = list(target.userrole_set.select_related('role').values_list('role__name', flat=True))
        if user_has_permission(viewer, 'view_permission'):
            perms = Permission.objects.filter(role__userrole__user=target).distinct()
            context['permissions'] = perms.values_list('codename', flat=True)
        if user_has_permission(viewer, 'view_auditlog'):
            context['logs'] = AuditLog.objects.filter(actor=target).order_by('-timestamp')[:10]
            context['all_logs_url'] = reverse_lazy('audit_log_list') + f'?actor={target.id}'
        return context

@method_decorator(require_permission('change_user'), name='dispatch')
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']
    template_name = 'user_form.html'

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target = self.get_object()
        context['require_current'] = self.request.user.pk == target.pk
        context['roles'] = Role.objects.filter(company=target.company)
        can_add_role = user_has_permission(self.request.user, 'add_role')
        can_change_role = user_has_permission(self.request.user, 'change_role')
        if can_add_role or can_change_role:
            context['permissions'] = Permission.objects.all()
        else:
            context['permissions'] = Permission.objects.none()
        context['can_add_role'] = can_add_role
        context['can_change_role'] = can_change_role
        user_role = target.userrole_set.filter(company=target.company).first()
        if user_role:
            context['assigned_ids'] = set(user_role.role.permissions.values_list('id', flat=True))
        else:
            context['assigned_ids'] = set()
        context['username'] = target.username
        context['email'] = target.email
        context['first_name'] = target.first_name
        context['last_name'] = target.last_name
        return context

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['username'] = form.data.get('username', '')
        context['email'] = form.data.get('email', '')
        context['first_name'] = form.data.get('first_name', '')
        context['last_name'] = form.data.get('last_name', '')
        return self.render_to_response(context)

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
        can_change_role = user_has_permission(self.request.user, 'change_role')
        if role_id == 'new':
            if not can_add_role:
                return HttpResponseForbidden()
            role_name = self.request.POST.get('new_role_name')
            role = Role.objects.create(name=role_name, company=company)
            perm_ids = self.request.POST.getlist('permissions')
            role.permissions.set(Permission.objects.filter(id__in=perm_ids))
        elif role_id:
            role = get_object_or_404(Role, pk=role_id, company=company)
            if can_change_role:
                perm_ids = self.request.POST.getlist('permissions')
                role.permissions.set(Permission.objects.filter(id__in=perm_ids))
        else:
            role = None
        if role:
            UserRole.objects.update_or_create(user=target, company=company, defaults={'role': role})
        log_action(
            self.request.user,
            'user_update',
            target,
            request_type=self.request.method,
            company=self.request.user.company,
        )
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
            log_action(
                request.user,
                'password_change',
                target,
                request_type=request.method,
                company=request.user.company,
            )
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
class RoleListView(LoginRequiredMixin, AdvancedListMixin, TemplateView):
    template_name = 'role_list.html'
    model = Role
    search_fields = ['name', 'description']
    default_sort = 'name'

    def base_queryset(self):
        return Role.objects.filter(company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = True
        context['filters'] = []
        context['sort_options'] = [
            ('name', 'Name'),
            ('description', 'Description'),
        ]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        context['can_add_role'] = user_has_permission(self.request.user, 'add_role')
        context['can_change_role'] = user_has_permission(self.request.user, 'change_role')
        return context


@method_decorator(require_permission('add_role'), name='dispatch')
class RoleCreateView(LoginRequiredMixin, View):
    def get(self, request):
        permissions = Permission.objects.all()
        context = {
            'permissions': permissions,
            'role': None,
            'name': '',
            'description': '',
        }
        return render(request, 'role_form.html', context)

    def post(self, request):
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if not name:
            permissions = Permission.objects.all()
            context = {
                'permissions': permissions,
                'error': 'Name required',
                'name': name,
                'description': description,
                'role': None,
            }
            return render(request, 'role_form.html', context)
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
        context = {
            'role': role,
            'permissions': perms,
            'assigned_ids': assigned,
            'name': role.name,
            'description': role.description or '',
        }
        return render(request, 'role_form.html', context)

    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk, company=request.user.company)
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if not name:
            perms = Permission.objects.all()
            assigned = set(int(i) for i in request.POST.getlist('permissions'))
            context = {
                'role': role,
                'permissions': perms,
                'assigned_ids': assigned,
                'error': 'Name required',
                'name': name,
                'description': description,
            }
            return render(request, 'role_form.html', context)
        role.name = name
        role.description = description
        role.save()
        perm_ids = request.POST.getlist('permissions')
        role.permissions.set(Permission.objects.filter(id__in=perm_ids))
        return redirect('role_list')


@method_decorator(require_permission('view_auditlog'), name='dispatch')
class AuditLogListView(LoginRequiredMixin, AdvancedListMixin, TemplateView):
    template_name = 'audit_log_list.html'
    model = AuditLog
    search_fields = ['actor__username', 'action', 'request_type', 'company__name']
    filter_fields = ['request_type', 'actor']
    default_sort = '-timestamp'

    def base_queryset(self):
        qs = AuditLog.objects.select_related('actor', 'target_user', 'company')
        if not self.request.user.is_superuser:
            qs = qs.filter(company=self.request.user.company)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = True
        context['sort_options'] = [
            ('-timestamp', 'Newest'),
            ('timestamp', 'Oldest'),
            ('actor__username', 'User'),
            ('action', 'Action'),
            ('request_type', 'Type'),
        ]
        # Show every user in the current company (or all users for superusers)
        if self.request.user.is_superuser:
            users_qs = User.objects.all()
        else:
            users_qs = User.objects.filter(company=self.request.user.company)
        user_options = [{'val': '', 'label': 'All'}]
        for u in users_qs:
            user_options.append({'val': str(u.pk), 'label': u.username})
        context['filters'] = [
            {
                'name': 'request_type',
                'label': 'Type',
                'current': self.request.GET.get('request_type', ''),
                'options': [
                    {'val': '', 'label': 'All'},
                    {'val': 'GET', 'label': 'GET'},
                    {'val': 'POST', 'label': 'POST'},
                    {'val': 'PUT', 'label': 'PUT'},
                    {'val': 'DELETE', 'label': 'DELETE'},
                ],
            },
            {
                'name': 'actor',
                'label': 'User',
                'current': self.request.GET.get('actor', ''),
                'options': user_options,
            },
        ]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        return context


@method_decorator(require_permission('view_auditlog'), name='dispatch')
class AuditLogDetailView(LoginRequiredMixin, TemplateView):
    """Display a single audit log entry with parsed JSON details."""

    template_name = 'audit_log_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log = get_object_or_404(AuditLog, pk=self.kwargs['pk'])
        if not self.request.user.is_superuser and log.company != self.request.user.company:
            raise PermissionDenied
        context['log'] = log
        try:
            details_dict = json.loads(log.details) if log.details else None
        except json.JSONDecodeError:
            details_dict = None
        if details_dict is not None:
            detail_rows = []
            for key, value in details_dict.items():
                if isinstance(value, (dict, list)):
                    pretty = json.dumps(value, indent=2)
                else:
                    pretty = value
                detail_rows.append((key, pretty))
            context['detail_rows'] = detail_rows
        return context

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
        log_action(
            request.user,
            'logout',
            request_type=request.method,
            company=request.user.company,
        )
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)

