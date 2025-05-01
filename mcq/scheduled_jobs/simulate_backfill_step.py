import math
import random
from datetime import timedelta, datetime as dt
from django.utils.timezone import make_aware, now
from mcq.models import Profile
from mcq.management.commands.create_fake_users import Command as CreateUsersCommand
from mcq.management.commands.simulate_quiz_activity import Command as SimulateQuizCommand

# Configurable growth target
TOTAL_USERS = 300

def simulate_backfill_step(sim_datetime, total_days=30):
    sim_datetime = make_aware(sim_datetime)
    today = now().date()
    target_start_date = today - timedelta(days=total_days)
    day_index = (sim_datetime.date() - target_start_date).days

    # Skip if day_index is invalid
    if day_index < 0 or day_index >= total_days:
        print(f"⚠️ Day index {day_index} out of range for {total_days} days.")
        return

    # Distribute growth over total_days using a linear ramp
    def user_count_on_day(d):
        base = 1.0 + 14.0 * (d / (total_days - 1))  # grows from 1 → 15
        return base

    # Sum all growth weights to normalize
    growth_weights = [user_count_on_day(d) for d in range(total_days)]
    total_weight = sum(growth_weights)
    daily_fraction = growth_weights[day_index] / total_weight
    users_to_add = math.ceil(TOTAL_USERS * daily_fraction)

    if users_to_add > 0:
        print(f"👤 Creating {users_to_add} simulated users on day {day_index + 1} / {total_days}")
        create_cmd = CreateUsersCommand()
        create_cmd.handle(count=users_to_add)
    else:
        print(f"✅ No users to add for day {day_index + 1}")

    # Simulate quizzes
    profiles = list(Profile.objects.filter(is_simulated=True))
    active_profiles = random.sample(profiles, k=int(0.7 * len(profiles))) if profiles else []

    simulate_cmd = SimulateQuizCommand()
    for profile in active_profiles:
        num_attempts = random.randint(1, 20)
        simulate_cmd.handle_for_profile(
            profile,
            num_attempts,
            num_attempts,
            10,
            sim_datetime
        )

    print(f"✅ Simulated {len(active_profiles)} active users at {sim_datetime.strftime('%Y-%m-%d %H:%M')}")
