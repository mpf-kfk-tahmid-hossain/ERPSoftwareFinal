from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Company, Role, UserRole

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

