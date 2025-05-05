from django.core.management.base import BaseCommand
from mcq.models import Profile, QuizAttempt, QuizResponse, Question
import random
from django.utils.timezone import now
from datetime import timedelta
import sys

class Command(BaseCommand):
    help = "Simulate hourly quiz attempts for all is_simulated=True users with a 50% chance."

    def handle(self, *args, **options):
        simulated_profiles = list(Profile.objects.filter(is_simulated=True))
        total_users = len(simulated_profiles)
        questions = list(Question.objects.all())
        questions_per_attempt = 10
        total_attempts = 0

        if len(questions) < questions_per_attempt:
            self.stdout.write(self.style.ERROR("❌ Not enough questions to simulate quiz attempts."))
            return

        self.stdout.write(self.style.SUCCESS(f"👥 Simulating activity for {total_users} simulated users...\n"))

        for i, profile in enumerate(simulated_profiles, 1):
            attempts_made = False

            if random.random() < 0.5:
                num_attempts = random.randint(0, 3)
                for _ in range(num_attempts):
                    total_attempts += 1
                    self.simulate_attempt(profile, questions, questions_per_attempt)
                    attempts_made = True

                if attempts_made:
                    profile.update_chain()

        self.print_progress(i, total_users)

        self.stdout.write("\n")
        self.stdout.write(self.style.SUCCESS(f"✅ Finished. Simulated {total_attempts} quiz attempts."))

    def simulate_attempt(self, profile, all_questions, num_questions):
        attempt_accuracy = min(1.0, max(0.0, random.gauss(profile.accuracy_mean, profile.accuracy_stddev)))
        selected_questions = random.sample(all_questions, num_questions)
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

        time_taken = random.randint(num_questions * 5, num_questions * 20)
        attempt_time = now() - timedelta(minutes=random.randint(0, 59))

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

    def print_progress(self, current, total):
        percent = int((current / total) * 100)
        bar = ('#' * (percent // 2)).ljust(50)
        sys.stdout.write(f'\r🔄 Progress: [{bar}] {percent}% ({current}/{total} users)')
        sys.stdout.flush()
