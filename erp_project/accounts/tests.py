from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Company, Role, UserRole, Permission

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
        from accounts.models import AuditLog
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


