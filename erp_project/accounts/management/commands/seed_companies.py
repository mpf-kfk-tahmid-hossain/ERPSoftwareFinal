import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from erp_project.accounts.models import Company, Role, Permission, UserRole
from faker import Faker

User = get_user_model()

class Command(BaseCommand):
    help = 'Create demo companies with random users and roles.'

    def handle(self, *args, **options):
        fake = Faker()
        perms = list(Permission.objects.all())
        if not perms:
            for i in range(5):
                perms.append(Permission.objects.create(codename=f'perm_{i}'))
        for idx in range(1, 11):
            company = Company.objects.create(
                name=fake.company(),
                code=f"C{idx:02d}",
                address=fake.address()
            )
            roles = []
            for r in range(3):
                role = Role.objects.create(
                    name=fake.job().replace("/", "-")[:50],
                    company=company
                )
                role.permissions.set(random.sample(perms, random.randint(1, len(perms))))
                roles.append(role)
            for u in range(random.randint(20, 100)):
                username = fake.unique.user_name()
                user = User.objects.create_user(username=username, password='pass', company=company)
                role = random.choice(roles)
                UserRole.objects.create(user=user, role=role, company=company)
        self.stdout.write(self.style.SUCCESS('Seeded companies and users'))
