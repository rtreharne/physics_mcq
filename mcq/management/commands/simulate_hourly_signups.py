from django.core.management.base import BaseCommand
from django.utils.timezone import now
from mcq.management.commands.create_fake_users import Command as CreateFakeUsersCommand
import random

class Command(BaseCommand):
    help = "Simulates hourly user signups (0–4) between 08:00 and 20:00 using the create_fake_users command."

    def handle(self, *args, **kwargs):
        current_hour = now().hour
        print(f"Current hour: {current_hour}")

        if current_hour < 6 or current_hour >= 20:
            self.stdout.write("⏰ Outside of active signup window (08:00–20:00). No users created.")
            return

        num_users = random.randint(0, 4)
        if num_users == 0:
            self.stdout.write("🛑 No simulated users created this hour.")
            return

        self.stdout.write(f"👥 Creating {num_users} simulated user(s)...")

        # Call your existing logic
        CreateFakeUsersCommand().handle(count=num_users)

        self.stdout.write(self.style.SUCCESS("✅ Hourly simulated signups complete."))
