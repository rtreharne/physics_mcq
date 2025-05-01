from django.core.management.base import BaseCommand
from mcq.models import Profile, QuizAttempt, QuizResponse, Question
import random
from django.utils.timezone import now
from datetime import datetime, time
from django.utils.timezone import make_aware

class Command(BaseCommand):
    help = "Simulates quiz attempts for all is_simulated=True users."

    def add_arguments(self, parser):
        parser.add_argument('--min', type=int, default=2, help="Minimum attempts per user")
        parser.add_argument('--max', type=int, default=8, help="Maximum attempts per user")
        parser.add_argument('--questions', type=int, default=10, help="Questions per attempt")

    def handle(self, *args, **options):
        min_attempts = options['min']
        max_attempts = options['max']
        num_questions = options['questions']

        simulated_profiles = Profile.objects.filter(is_simulated=True)
        questions = list(Question.objects.all())

        if len(questions) < num_questions:
            self.stdout.write(self.style.ERROR("❌ Not enough questions in the database to simulate attempts."))
            return

        total_attempts = 0

        for profile in simulated_profiles:
            total_attempts += self.simulate_for_profile(profile, min_attempts, max_attempts, num_questions)

        self.stdout.write(self.style.SUCCESS(f"✅ Simulated {total_attempts} quiz attempts for {simulated_profiles.count()} users."))

    def handle_for_profile(self, profile, min_attempts, max_attempts, num_questions=10, timestamp=None):
        """Simulate quiz attempts for a single Profile instance."""
        return self.simulate_for_profile(profile, min_attempts, max_attempts, num_questions, timestamp)

    def simulate_for_profile(self, profile, min_attempts, max_attempts, num_questions, timestamp=None):
        questions = list(Question.objects.all())

        attempt_accuracy = min(1.0, max(0.0, random.gauss(profile.accuracy_mean, profile.accuracy_stddev)))

        if len(questions) < num_questions:
            return 0

        num_attempts = random.randint(min_attempts, max_attempts)
        total_created = 0

        for _ in range(num_attempts):
            selected_questions = random.sample(questions, num_questions)
            responses = []
            num_correct = 0

            for question in selected_questions:
                correct_option = question.correct_option
                if random.random() < attempt_accuracy:
                    user_answer = correct_option
                    correct = True
                else:
                    options = ['A', 'B', 'C', 'D']
                    options.remove(correct_option)
                    user_answer = random.choice(options)
                    correct = False

                responses.append((question, user_answer, correct))
                if correct:
                    num_correct += 1

            score_percent = int(round((num_correct / num_questions) * 100))


            time_taken = random.randint(num_questions * 5, num_questions * 20)

            if timestamp:
                base_date = timestamp.date()
                attempt_time = self.get_weighted_random_time(base_date)
            else:
                attempt_time = now()

            attempt = QuizAttempt.objects.create(
                user=profile.user,
                date_taken=attempt_time,
                score=num_correct,
                total_questions=num_questions,
                time_taken_seconds=time_taken
            )

            for question, user_answer, correct in responses:
                QuizResponse.objects.create(
                    attempt=attempt,
                    question=question,
                    user_answer=user_answer,
                    correct=correct
                )

            total_created += 1

        return total_created

    def get_weighted_random_time(self, base_date):
        """Return a timezone-aware datetime with realistic peak-hour weighting."""
        weighted_hours = (
            [random.randint(8, 10)] * 1 +
            [random.randint(11, 13)] * 2 +
            [random.randint(14, 16)] * 1 +
            [random.randint(17, 21)] * 5 +
            [random.randint(6, 23)]       # rare fallback
        )
        chosen_hour = random.choice(weighted_hours)
        chosen_minute = random.randint(0, 59)

        naive_dt = datetime.combine(base_date, time(chosen_hour, chosen_minute))
        return make_aware(naive_dt)
