from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mcq.models import Profile
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone
from mcq.utils.username_generator import generate_anonymous_username

fake = Faker()

class Command(BaseCommand):
    help = "Creates or updates simulated fake users with Profile data."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help="Number of fake users to create or update.")

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        processed = 0
        start_date = timezone.now() - timedelta(days=120)

        for _ in range(count):
            # Generate consistent user details
            full_name = fake.name()
            first_name, last_name = full_name.split(' ', 1)
            username_base = f"{first_name}.{last_name}".lower().replace(" ", "").replace("'", "")
            username = username_base
            counter = 1

            # Ensure username is unique
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1

            email = f"{username}@example.com"
            signup_date = start_date + timedelta(days=random.randint(0, 120))

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123'
            )
            user.first_name = first_name
            user.last_name = last_name
            user.date_joined = signup_date
            user.save()

            # Get or create profile
            profile, _ = Profile.objects.get_or_create(user=user)

            # Generate a unique anonymous name if not already set
            if not profile.anonymous_name:
                anon_name = generate_anonymous_username()
                while Profile.objects.filter(anonymous_name=anon_name).exists():
                    anon_name = generate_anonymous_username()
                profile.anonymous_name = anon_name

            # Assign simulated values
            profile.chain_length = 1
            profile.points = 0
            profile.is_simulated = True
            profile.accuracy_mean=random.uniform(0.5, 0.9)
            profile.accuracy_stddev=random.uniform(0.05, 0.2)
            profile.save()

            processed += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Processed {processed} fake users."))
