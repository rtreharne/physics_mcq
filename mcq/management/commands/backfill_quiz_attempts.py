from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from mcq.models import Profile, Question, QuizAttempt, QuizResponse
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = "Generates historical quiz attempts for all simulated users."

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Number of past days to simulate.')

    def handle(self, *args, **options):
        days = options['days']
        today = datetime.now().date()
        simulated_profiles = Profile.objects.filter(is_simulated=True)
        questions = list(Question.objects.all())

        if len(questions) < 10:
            self.stdout.write(self.style.ERROR("❌ Not enough questions in the database."))
            return

        total_attempts = 0

        for day_offset in range(days):
            day = today - timedelta(days=day_offset)
            self.stdout.write(self.style.NOTICE(f"\n📅 Simulating {day.strftime('%Y-%m-%d')}..."))

            for profile in simulated_profiles:
                num_attempts = random.randint(0, 10)
                self.stdout.write(f"👤 {profile.anonymous_name} — {num_attempts} attempt(s)")

                if num_attempts == 0:
                    continue

                for _ in range(num_attempts):
                    timestamp = self.generate_realistic_time(day)
                    selected_questions = random.sample(questions, 10)

                    correct_answers = 0
                    responses = []

                    mean = profile.accuracy_mean if profile.accuracy_mean is not None else 0.7
                    stddev = profile.accuracy_stddev if profile.accuracy_stddev is not None else 0.1
                    accuracy = min(1.0, max(0.0, random.gauss(mean, stddev)))

                    for question in selected_questions:
                        if random.random() < accuracy:
                            user_answer = question.correct_option
                            correct = True
                        else:
                            options = ['A', 'B', 'C', 'D']
                            options.remove(question.correct_option)
                            user_answer = random.choice(options)
                            correct = False
                        responses.append((question, user_answer, correct))
                        if correct:
                            correct_answers += 1

                    score = int((correct_answers / 10) * 100)
                    chain_length = profile.chain_length or 1
                    bonus = min(chain_length, 7)
                    points = score * bonus
                    time_taken = random.randint(30, 180)

                    attempt = QuizAttempt.objects.create(
                        user=profile.user,
                        score=score,
                        total_questions=10,
                        time_taken_seconds=time_taken,
                        points=points,
                        date_taken=make_aware(timestamp)
                    )

                    for q, ans, correct in responses:
                        QuizResponse.objects.create(
                            attempt=attempt,
                            question=q,
                            user_answer=ans,
                            correct=correct
                        )

                    total_attempts += 1

                self.stdout.write(self.style.SUCCESS(
                    f"✅ Saved {num_attempts} attempt(s) for {profile.anonymous_name}"
                ))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Created {total_attempts} quiz attempts over {days} days."))

    def generate_realistic_time(self, day):
        # Simulate realistic student usage times (heavy between 9am–9pm)
        hour_weights = [0]*6 + [1]*2 + [2]*3 + [4]*4 + [6]*5 + [4]*4

        hour = random.choices(range(24), weights=hour_weights, k=1)[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return datetime.combine(day, datetime.min.time()).replace(hour=hour, minute=minute, second=second)
