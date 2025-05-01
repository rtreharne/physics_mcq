from django.core.management.base import BaseCommand
from mcq.models import Profile, QuizAttempt
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Deletes all simulated users, their profiles, quiz attempts, and related data."

    def handle(self, *args, **options):
        simulated_profiles = Profile.objects.filter(is_simulated=True)
        user_ids = simulated_profiles.values_list('user_id', flat=True)

        # Delete quiz attempts
        quiz_attempts_deleted, _ = QuizAttempt.objects.filter(user_id__in=user_ids).delete()

        # Delete users (which cascades to Profile via OneToOneField)
        users_deleted, _ = User.objects.filter(id__in=user_ids).delete()

        self.stdout.write(self.style.SUCCESS(
            f"🗑️ Deleted {users_deleted} simulated users and {quiz_attempts_deleted} quiz attempts."
        ))
