"""
URL configuration for erp_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import CustomLogoutView
from accounts.views import (
    CustomLoginView, DashboardView, CompanyCreateView, CompanyListView,
    CompanyDetailView, CompanyUpdateView, UserListView, CompanyUserCreateView,
    UserDetailView, UserUpdateView, UserToggleActiveView, WhoAmIView, DashboardAPI,
    RoleListView, RoleCreateView, RoleUpdateView, change_password_view,
    AuditLogListView, AuditLogDetailView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('companies/', CompanyListView.as_view(), name='company_list'),
    path('companies/add/', CompanyCreateView.as_view(), name='company_add'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    path('companies/<int:pk>/edit/', CompanyUpdateView.as_view(), name='company_edit'),
    path('companies/<int:company_id>/users/', UserListView.as_view(), name='user_list'),
    path('companies/<int:company_id>/users/add/', CompanyUserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/toggle/', UserToggleActiveView.as_view(), name='user_toggle'),
    path('users/<int:pk>/password/', change_password_view, name='user_change_password'),
    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/add/', RoleCreateView.as_view(), name='role_add'),
    path('roles/<int:pk>/edit/', RoleUpdateView.as_view(), name='role_edit'),
    path('audit-logs/', AuditLogListView.as_view(), name='audit_log_list'),
    path('audit-logs/<int:pk>/', AuditLogDetailView.as_view(), name='audit_log_detail'),
    path('api/whoami/', WhoAmIView.as_view(), name='whoami'),
    path('api/dashboard/', DashboardAPI.as_view(), name='dashboard_api'),
    path('', DashboardView.as_view(), name='dashboard'),
]

from accounts.views import permission_denied_view
handler403 = permission_denied_view

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

