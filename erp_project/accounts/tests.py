from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Company, Role, UserRole, Permission, AuditLog
from .utils import log_action

User = get_user_model()

class OnboardingTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='pass')

    def test_superuser_login_and_create_company(self):
        login = self.client.login(username='admin', password='pass')
        self.assertTrue(login)
        response = self.client.post(reverse('company_add'), {'name': 'Acme', 'code': 'AC', 'address': 'Addr'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Company.objects.filter(code='AC').exists())

    def test_company_detail_view(self):
        company = Company.objects.create(name='Beta', code='B', address='')
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('company_detail', args=[company.id]))
        self.assertEqual(resp.status_code, 200)

    def test_create_user_and_toggle_active(self):
        company = Company.objects.create(name='Beta', code='B1', address='')
        self.client.login(username='admin', password='pass')
        resp = self.client.post(reverse('user_add', args=[company.id]), {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(resp.status_code, 302)
        user = User.objects.get(username='newuser')
        self.assertTrue(UserRole.objects.filter(user=user, role__name='Admin').exists())
        toggle = self.client.post(reverse('user_toggle', args=[user.id]))
        self.assertEqual(toggle.status_code, 302)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'admin', 'password': 'pass'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')

    def test_superuser_can_logout_via_button(self):
        self.client.login(username='admin', password='pass')
        dashboard = self.client.get(reverse('dashboard'))
        self.assertContains(dashboard, reverse('logout'))
        logout_response = self.client.get(reverse('logout'))
        self.assertEqual(logout_response.status_code, 302)
        self.assertEqual(logout_response['Location'], reverse('login'))
        follow_up = self.client.get(reverse('dashboard'))
        self.assertEqual(follow_up.status_code, 302)

class PermissionTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='pass')
        self.company = Company.objects.create(name='TestCo', code='TC', address='')
        self.user = User.objects.create_user(username='employee', password='pass', company=self.company)

    def test_non_superuser_cannot_add_company(self):
        self.client.login(username='employee', password='pass')
        resp = self.client.get(reverse('company_add'))
        self.assertEqual(resp.status_code, 403)

    def test_non_admin_cannot_manage_users(self):
        self.client.login(username='employee', password='pass')
        resp = self.client.get(reverse('user_list', args=[self.company.id]))
        self.assertEqual(resp.status_code, 403)

class IntegrationFlowTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='pass')

    def test_happy_path_onboarding(self):
        self.client.login(username='admin', password='pass')
        self.client.post(reverse('company_add'), {'name': 'Acme', 'code': 'AC', 'address': 'A'})
        company = Company.objects.get(code='AC')
        resp = self.client.post(reverse('user_add', args=[company.id]), {
            'username': 'coadmin',
            'password1': 'pass12345',
            'password2': 'pass12345'
        })
        self.assertEqual(resp.status_code, 302)
        self.client.logout()
        login = self.client.login(username='coadmin', password='pass12345')
        self.assertTrue(login)
        dash = self.client.get(reverse('dashboard'))
        self.assertContains(dash, 'Welcome')

    def test_workflow_step_by_step(self):
        # Step 1: Superuser Authentication
        self.assertTrue(self.client.login(username='admin', password='pass'))

        # Step 2: Company Registration
        self.client.post(reverse('company_add'), {
            'name': 'StepCo', 'code': 'ST', 'address': 'Addr'
        })
        company = Company.objects.get(code='ST')
        other_company = Company.objects.create(name='OtherCo', code='OC', address='')

        # Step 3: Company Admin User Creation
        resp = self.client.post(reverse('user_add', args=[company.id]), {
            'username': 'adminuser',
            'password1': 'pass12345',
            'password2': 'pass12345'
        })
        self.assertEqual(resp.status_code, 302)
        new_user = User.objects.get(username='adminuser')
        self.assertTrue(UserRole.objects.filter(user=new_user, role__name='Admin', company=company).exists())

        # Step 4: Company Admin Authentication
        self.client.logout()
        self.assertTrue(self.client.login(username='adminuser', password='pass12345'))

        # Step 5: Company Admin Dashboard Access
        dash = self.client.get(reverse('dashboard'))
        self.assertEqual(dash.status_code, 200)

        # Step 6: Role and Permission Enforcement
        deny = self.client.get(reverse('company_add'))
        self.assertEqual(deny.status_code, 403)
        other_access = self.client.get(reverse('user_list', args=[other_company.id]))
        self.assertEqual(other_access.status_code, 403)

        # Step 7: Session Management
        self.client.logout()
        dash_again = self.client.get(reverse('dashboard'))
        self.assertEqual(dash_again.status_code, 302)


class CompanyUserLoginTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='pass')
        self.company = Company.objects.create(name='NavCo', code='NC', address='')
        self.admin_role = Role.objects.get(name='Admin')
        view_perm = Permission.objects.get_or_create(codename='view_user')[0]
        self.admin_role.permissions.add(view_perm)

    def test_user_add_hashes_password(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.post(reverse('user_add', args=[self.company.id]), {
            'username': 'coadmin',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123'
        })
        if resp.status_code != 302:
            self.fail(f"Form errors: {resp.context['form'].errors}")
        user = User.objects.get(username='coadmin')
        self.assertTrue(user.password.startswith('argon2$'))

    def test_company_user_navbar_and_user_list_access(self):
        user = User.objects.create_user(username='emp', password='emp123', company=self.company)
        UserRole.objects.create(user=user, role=self.admin_role, company=self.company)
        login = self.client.login(username='emp', password='emp123')
        self.assertTrue(login)
        dash = self.client.get(reverse('dashboard'))
        self.assertContains(dash, reverse('user_list', args=[self.company.id]))
        list_resp = self.client.get(reverse('user_list', args=[self.company.id]))
        self.assertEqual(list_resp.status_code, 200)


class PermissionDecoratorTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='PermCo', code='PC', address='')
        self.superuser = User.objects.create_superuser(username='admin', password='pass')
        self.user = User.objects.create_user(username='bob', password='pass', company=self.company)
        self.role = Role.objects.create(name='Staff', company=self.company)
        UserRole.objects.create(user=self.user, role=self.role, company=self.company)

    def test_superuser_creating_user(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('user_add', args=[self.company.id]))
        self.assertEqual(resp.status_code, 200)

    def test_normal_user_with_permission_creating_user(self):
        perm = Permission.objects.get_or_create(codename='add_user')[0]
        self.role.permissions.add(perm)
        self.client.login(username='bob', password='pass')
        resp = self.client.get(reverse('user_add', args=[self.company.id]))
        self.assertEqual(resp.status_code, 200)

    def test_user_denied_without_permission(self):
        self.client.login(username='bob', password='pass')
        resp = self.client.get(reverse('user_add', args=[self.company.id]))
        self.assertEqual(resp.status_code, 403)


class PasswordChangeTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='PassCo', code='PCO', address='')
        role = Role.objects.create(name='Staff', company=self.company)
        self.user = User.objects.create_user(username='alice', password='pass', company=self.company)
        self.other = User.objects.create_user(username='other', password='pass', company=self.company)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        UserRole.objects.create(user=self.other, role=role, company=self.company)
        self.role = role

    def test_change_own_password(self):
        self.client.login(username='alice', password='pass')
        resp = self.client.post(
            reverse('user_change_password', args=[self.user.id]),
            {
                'current_password': 'pass',
                'password1': 'newpass',
                'password2': 'newpass',
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.client.logout()
        self.assertTrue(self.client.login(username='alice', password='newpass'))

    def test_change_other_requires_permission(self):
        self.client.login(username='alice', password='pass')
        resp = self.client.post(
            reverse('user_change_password', args=[self.other.id]),
            {'password1': 'x', 'password2': 'x'},
        )
        self.assertEqual(resp.status_code, 403)
        perm = Permission.objects.get_or_create(codename='user_can_change_password')[0]
        self.role.permissions.add(perm)
        resp2 = self.client.post(
            reverse('user_change_password', args=[self.other.id]),
            {'password1': 'x2', 'password2': 'x2'},
        )
        self.assertEqual(resp2.status_code, 302)
        self.client.logout()
        self.assertTrue(self.client.login(username='other', password='x2'))

    def test_change_own_password_requires_current(self):
        self.client.login(username='alice', password='pass')
        resp = self.client.post(
            reverse('user_change_password', args=[self.user.id]),
            {'current_password': 'wrong', 'password1': 'bad', 'password2': 'bad'},
        )
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('pass'))

    def test_change_other_logs_action(self):
        perm = Permission.objects.get_or_create(codename='user_can_change_password')[0]
        self.role.permissions.add(perm)
        self.client.login(username='alice', password='pass')
        self.client.post(
            reverse('user_change_password', args=[self.other.id]),
            {'password1': 'x2', 'password2': 'x2'},
        )
        from erp_project.accounts.models import AuditLog
        self.assertTrue(AuditLog.objects.filter(actor=self.user, target_user=self.other, action='password_change').exists())


class UserEditSecurityTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='EditCo', code='EC', address='')
        role = Role.objects.create(name='Staff', company=self.company)
        self.user = User.objects.create_user(username='charlie', password='pass', company=self.company)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.role = role

    def test_edit_self_denied_without_permission(self):
        self.client.login(username='charlie', password='pass')
        resp = self.client.get(reverse('user_edit', args=[self.user.id]))
        self.assertEqual(resp.status_code, 403)

    def test_edit_self_requires_current_password(self):
        perm = Permission.objects.get_or_create(codename='change_user')[0]
        self.role.permissions.add(perm)
        self.client.login(username='charlie', password='pass')
        resp = self.client.post(
            reverse('user_edit', args=[self.user.id]),
            {
                'username': 'newcharlie',
                'email': self.user.email,
                'first_name': '',
                'last_name': '',
                'current_password': 'wrong',
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'charlie')

    def test_edit_self_with_password(self):
        perm = Permission.objects.get_or_create(codename='change_user')[0]
        self.role.permissions.add(perm)
        self.client.login(username='charlie', password='pass')
        resp = self.client.post(
            reverse('user_edit', args=[self.user.id]),
            {
                'username': 'newcharlie',
                'email': self.user.email,
                'first_name': '',
                'last_name': '',
                'current_password': 'pass',
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newcharlie')


class ButtonVisibilityTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='BtnCo', code='BC', address='')
        staff_role = Role.objects.create(name='Staff', company=self.company)
        admin_role = Role.objects.create(name='Admin', company=self.company)
        perm_edit = Permission.objects.get_or_create(codename='change_user')[0]
        perm_pass = Permission.objects.get_or_create(codename='user_can_change_password')[0]
        view_perm = Permission.objects.get_or_create(codename='view_user')[0]
        admin_role.permissions.add(perm_edit, perm_pass, view_perm)
        staff_role.permissions.add(view_perm)
        self.user = User.objects.create_user(username='dave', password='pass', company=self.company)
        self.admin = User.objects.create_superuser(username='admin2', password='pass')
        self.admin.company = self.company
        self.admin.save()
        UserRole.objects.create(user=self.user, role=staff_role, company=self.company)
        UserRole.objects.create(user=self.admin, role=admin_role, company=self.company)

    def test_buttons_hidden_without_permission(self):
        self.client.login(username='dave', password='pass')
        resp = self.client.get(reverse('user_detail', args=[self.user.id]))
        self.assertNotContains(resp, reverse('user_edit', args=[self.user.id]))
        self.assertContains(resp, reverse('user_change_password', args=[self.user.id]))

    def test_admin_sees_management_buttons(self):
        """Admin user should see edit, password, and toggle controls."""
        self.client.login(username='admin2', password='pass')
        resp = self.client.get(reverse('user_detail', args=[self.user.id]))
        self.assertContains(resp, reverse('user_edit', args=[self.user.id]))
        self.assertContains(resp, reverse('user_change_password', args=[self.user.id]))
        self.assertContains(resp, reverse('user_toggle', args=[self.user.id]))

    def test_target_permissions_do_not_grant_buttons(self):
        """Viewer permissions determine buttons, not the target user's roles."""
        target = User.objects.create_user(username='targetp', password='pass', company=self.company)
        role = Role.objects.create(name='Priv', company=self.company)
        perm_edit = Permission.objects.get_or_create(codename='change_user')[0]
        role.permissions.add(perm_edit)
        UserRole.objects.create(user=target, role=role, company=self.company)
        self.client.login(username='dave', password='pass')
        resp = self.client.get(reverse('user_detail', args=[target.id]))
        self.assertNotContains(resp, reverse('user_edit', args=[target.id]))


class AuditMiddlewareTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='auditor', password='pass')

    def test_login_and_logout_logged(self):
        self.client.post(reverse('login'), {'username': 'auditor', 'password': 'pass'})
        from erp_project.accounts.models import AuditLog
        log = AuditLog.objects.get(actor=self.user, action='login')
        self.assertEqual(log.request_type, 'POST')
        self.assertEqual(log.company, self.user.company)
        self.client.get(reverse('logout'))
        log = AuditLog.objects.get(actor=self.user, action='logout')
        self.assertEqual(log.request_type, 'GET')


class RoleChangeTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='RoleCo', code='RC', address='')
        self.user = User.objects.create_user(username='target', password='pass', company=self.company)
        self.admin = User.objects.create_user(username='roleadmin', password='pass', company=self.company)
        self.admin_role = Role.objects.get(name='Admin')
        perm = Permission.objects.get_or_create(codename='change_user')[0]
        self.admin_role.permissions.add(perm)
        UserRole.objects.create(user=self.admin, role=self.admin_role, company=self.company)

    def test_change_user_role(self):
        new_role = Role.objects.create(name='Staff', company=self.company)
        self.client.login(username='roleadmin', password='pass')
        resp = self.client.post(
            reverse('user_edit', args=[self.user.id]),
            {
                'username': 'target',
                'email': '',
                'first_name': '',
                'last_name': '',
                'role': new_role.id,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(UserRole.objects.filter(user=self.user, role=new_role).exists())


class AddRolePermissionTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Perm2Co', code='P2', address='')
        self.role = Role.objects.create(name='Staff', company=self.company)
        add_user_perm = Permission.objects.get_or_create(codename='add_user')[0]
        self.role.permissions.add(add_user_perm)
        self.user = User.objects.create_user(username='creator', password='pass', company=self.company)
        UserRole.objects.create(user=self.user, role=self.role, company=self.company)

    def test_form_hides_add_role_without_permission(self):
        self.client.login(username='creator', password='pass')
        resp = self.client.get(reverse('user_add', args=[self.company.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Create new role')

    def test_form_shows_add_role_with_permission(self):
        add_role_perm = Permission.objects.get_or_create(codename='add_role')[0]
        self.role.permissions.add(add_role_perm)
        self.client.login(username='creator', password='pass')
        resp = self.client.get(reverse('user_add', args=[self.company.id]))
        self.assertContains(resp, 'Create new role')

    def test_post_new_role_without_permission_forbidden(self):
        self.client.login(username='creator', password='pass')
        resp = self.client.post(
            reverse('user_add', args=[self.company.id]),
            {
                'username': 'x',
                'password1': 'p@ssword1',
                'password2': 'p@ssword1',
                'role': 'new',
                'new_role_name': 'Temp',
            },
        )
        self.assertEqual(resp.status_code, 403)

    def test_post_new_role_with_permission(self):
        add_role_perm = Permission.objects.get_or_create(codename='add_role')[0]
        self.role.permissions.add(add_role_perm)
        self.client.login(username='creator', password='pass')
        resp = self.client.post(
            reverse('user_add', args=[self.company.id]),
            {
                'username': 'newu',
                'password1': 'p@ssword1',
                'password2': 'p@ssword1',
                'role': 'new',
                'new_role_name': 'TempRole',
                'permissions': [],
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Role.objects.filter(name='TempRole', company=self.company).exists())


class ChangeRolePermissionTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='PermEditCo', code='PEC', address='')
        self.admin_role = Role.objects.create(name='AdminRole', company=self.company)
        self.target_role = Role.objects.create(name='TargetRole', company=self.company)
        self.change_user_perm = Permission.objects.get_or_create(codename='change_user')[0]
        self.change_role_perm = Permission.objects.get_or_create(codename='change_role')[0]
        self.sample_perm = Permission.objects.get_or_create(codename='sample')[0]
        self.admin_role.permissions.add(self.change_user_perm, self.change_role_perm)
        self.target_role.permissions.add(self.sample_perm)
        self.admin = User.objects.create_user(username='adminp', password='pass', company=self.company)
        self.target = User.objects.create_user(username='targetp', password='pass', company=self.company)
        UserRole.objects.create(user=self.admin, role=self.admin_role, company=self.company)
        UserRole.objects.create(user=self.target, role=self.target_role, company=self.company)

    def test_edit_shows_permission_grid(self):
        self.client.login(username='adminp', password='pass')
        resp = self.client.get(reverse('user_edit', args=[self.target.id]))
        self.assertContains(resp, 'perm%s' % self.sample_perm.id)

    def test_edit_updates_role_permissions(self):
        new_perm = Permission.objects.get_or_create(codename='newp')[0]
        self.client.login(username='adminp', password='pass')
        resp = self.client.post(
            reverse('user_edit', args=[self.target.id]),
            {
                'username': 'targetp',
                'email': '',
                'first_name': '',
                'last_name': '',
                'role': self.target_role.id,
                'permissions': [str(new_perm.id)],
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(self.target_role.permissions.filter(id=new_perm.id).exists())


class AuditLogListTests(TestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name='AL1', code='AL1', address='')
        self.company2 = Company.objects.create(name='AL2', code='AL2', address='')
        role = Role.objects.create(name='Auditor', company=self.company1)
        perm = Permission.objects.get_or_create(codename='view_auditlog')[0]
        role.permissions.add(perm)
        self.user1 = User.objects.create_user(username='u1', password='pass', company=self.company1)
        self.user2 = User.objects.create_user(username='u2', password='pass', company=self.company2)
        UserRole.objects.create(user=self.user1, role=role, company=self.company1)
        log_action(self.user1, 'x', request_type='GET', company=self.company1)
        log_action(self.user2, 'y', request_type='POST', company=self.company2)

    def test_company_filtered_logs(self):
        self.client.login(username='u1', password='pass')
        resp = self.client.get(reverse('audit_log_list'))
        self.assertEqual(resp.context['page_obj'].paginator.count, 1)
        self.assertContains(resp, 'x')

    def test_actor_filter(self):
        other = User.objects.create_user(username='o1', password='pass', company=self.company1)
        log_action(other, 'z', request_type='GET', company=self.company1)
        self.client.login(username='u1', password='pass')
        resp = self.client.get(reverse('audit_log_list'), {'actor': other.id})
        self.assertEqual(resp.context['page_obj'].paginator.count, 1)
        self.assertContains(resp, 'z')

    def test_user_filter_shows_all_company_users(self):
        """Users without logs should still appear in the actor filter."""
        extra = User.objects.create_user(username='extra', password='pass', company=self.company1)
        self.client.login(username='u1', password='pass')
        resp = self.client.get(reverse('audit_log_list'))
        actor_opts = resp.context['filters'][1]['options']
        vals = [opt['val'] for opt in actor_opts]
        self.assertIn(str(extra.id), vals)


class AuditLogDetailTests(TestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name='D1', code='D1', address='')
        self.company2 = Company.objects.create(name='D2', code='D2', address='')
        role = Role.objects.create(name='Auditor', company=self.company1)
        perm = Permission.objects.get_or_create(codename='view_auditlog')[0]
        role.permissions.add(perm)
        self.user1 = User.objects.create_user(username='d1', password='pass', company=self.company1)
        self.user2 = User.objects.create_user(username='d2', password='pass', company=self.company2)
        UserRole.objects.create(user=self.user1, role=role, company=self.company1)
        self.log1 = AuditLog.objects.create(actor=self.user1, action='a', company=self.company1)
        self.log2 = AuditLog.objects.create(actor=self.user2, action='b', company=self.company2)

    def test_detail_allowed_same_company(self):
        self.client.login(username='d1', password='pass')
        resp = self.client.get(reverse('audit_log_detail', args=[self.log1.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'a')

    def test_detail_forbidden_other_company(self):
        self.client.login(username='d1', password='pass')
        resp = self.client.get(reverse('audit_log_detail', args=[self.log2.id]))
        self.assertEqual(resp.status_code, 403)


class UserListFeatureTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='SearchCo', code='SC', address='')
        perm = Permission.objects.get_or_create(codename='view_user')[0]
        role = Role.objects.get(name='Admin')
        role.permissions.add(perm)
        self.admin = User.objects.create_user(username='admin1', password='pass', company=self.company)
        UserRole.objects.create(user=self.admin, role=role, company=self.company)
        User.objects.create_user(username='alice', password='pass', company=self.company)
        User.objects.create_user(username='bob', password='pass', company=self.company)

    def test_search_filters_users(self):
        self.client.login(username='admin1', password='pass')
        resp = self.client.get(reverse('user_list', args=[self.company.id]), {'q': 'ali'})
        self.assertContains(resp, 'alice')
        self.assertNotContains(resp, 'bob')

    def test_sort_users_by_email_desc(self):
        self.client.login(username='admin1', password='pass')
        resp = self.client.get(reverse('user_list', args=[self.company.id]), {'sort': '-email'})
        users = list(resp.context['page_obj'])
        self.assertGreater(len(users), 1)
        emails = [u.email for u in users]
        self.assertEqual(emails, sorted(emails, reverse=True))


class CompanyListFeatureTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='pass')
        Company.objects.create(name='AlphaCo', code='A1', address='')
        Company.objects.create(name='BetaCo', code='B1', address='')

    def test_search_filters_companies(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('company_list'), {'q': 'Beta'})
        self.assertContains(resp, 'BetaCo')
        self.assertNotContains(resp, 'AlphaCo')

    def test_sort_companies_by_code(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('company_list'), {'sort': 'code'})
        companies = list(resp.context['page_obj'])
        codes = [c.code for c in companies]
        self.assertEqual(codes, sorted(codes))


class ProfilePictureDisplayTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='PicCo', code='PIC', address='')
        role = Role.objects.get(name='Admin')
        perm_add = Permission.objects.get_or_create(codename='add_user')[0]
        perm_view = Permission.objects.get_or_create(codename='view_user')[0]
        role.permissions.add(perm_add, perm_view)
        self.admin = User.objects.create_user(username='padmin', password='pass', company=self.company)
        UserRole.objects.create(user=self.admin, role=role, company=self.company)
        self.client.login(username='padmin', password='pass')

    def test_profile_picture_display(self):
        from io import BytesIO
        from PIL import Image
        img_io = BytesIO()
        Image.new('RGB', (1, 1)).save(img_io, format='JPEG')
        img = SimpleUploadedFile('pic.jpg', img_io.getvalue(), content_type='image/jpeg')
        resp = self.client.post(
            reverse('user_add', args=[self.company.id]),
            {
                'username': 'imguser',
                'password1': 'pass12345',
                'password2': 'pass12345',
                'profile_picture': img,
            }
        )
        if resp.status_code != 302:
            print('form errors', resp.context['form'].errors)
        self.assertEqual(resp.status_code, 302)
        user = User.objects.get(username='imguser')
        list_resp = self.client.get(reverse('user_list', args=[self.company.id]))
        self.assertContains(list_resp, user.profile_picture.url)
        detail_resp = self.client.get(reverse('user_detail', args=[user.id]))
        self.assertContains(detail_resp, user.profile_picture.url)


class TemplatePermissionFilterTests(TestCase):
    def test_templates_do_not_use_has_permission_filter(self):
        from pathlib import Path
        from django.conf import settings

        template_root = settings.BASE_DIR / 'templates'
        for tpl in template_root.rglob('*.html'):
            with self.subTest(template=tpl.name):
                content = tpl.read_text()
                self.assertNotIn('|has_permission', content)


class UserUpdateValidationTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='ValCo', code='VC', address='')
        self.user = User.objects.create_user(username='val', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perm = Permission.objects.get_or_create(codename='change_user')[0]
        role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='val', password='pass')

    def test_update_requires_required_fields(self):
        resp = self.client.post(reverse('user_edit', args=[self.user.id]), {
            'username': '',
            'email': '',
            'first_name': '',
            'last_name': '',
            'current_password': 'pass'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'This field is required')



