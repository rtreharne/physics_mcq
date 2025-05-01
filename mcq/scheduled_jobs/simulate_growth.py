import math
import random
from django.utils.timezone import now, timedelta
from mcq.models import Profile, QuizAttempt
from mcq.management.commands.create_fake_users import Command as CreateUsersCommand
from mcq.management.commands.simulate_quiz_activity import Command as SimulateQuizCommand
from django.db.models import Max

# --- Config ---
TOTAL_USER_CAP = 5000
GROWTH_MIDPOINT_HOUR = 360
GROWTH_RATE_K = 0.03

def logistic(t, L=TOTAL_USER_CAP, k=GROWTH_RATE_K, x0=GROWTH_MIDPOINT_HOUR):
    return L / (1 + math.exp(-k * (t - x0)))

def simulate_growth(current_datetime=None):
    now_time = current_datetime or now()
    current_date = now_time.date()

    # Fixed launch window
    LAUNCH_START = now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
    hours_since_launch = (now_time - LAUNCH_START).total_seconds() / 3600
    hours_before = max(0, hours_since_launch - 1)

    # Expected users at current and previous hour
    expected_now = logistic(hours_since_launch)
    expected_previous = logistic(hours_before)
    users_to_add = max(0, math.ceil(expected_now - expected_previous))

    if users_to_add > 0:
        print(f"👤 Creating {users_to_add} simulated users... (target: {int(expected_now)})")
        create_cmd = CreateUsersCommand()
        create_cmd.handle(count=users_to_add)
    else:
        print(f"✅ User growth saturated or unchanged at ~{int(expected_now)} users.")

    # Get all simulated profiles
    all_profiles = list(Profile.objects.filter(is_simulated=True))

    # ⛓️ Update chain streaks BEFORE quiz simulation
    print("⛓️ Updating chain streaks...")
    yesterday = current_date - timedelta(days=1)
    for profile in all_profiles:
        latest_attempt = QuizAttempt.objects.filter(user=profile.user).aggregate(Max('date_taken'))['date_taken__max']
        if latest_attempt:
            latest_date = latest_attempt.date()
            if profile.last_chain_date == current_date:
                continue
            elif profile.last_chain_date == yesterday and latest_date == current_date:
                profile.chain_length += 1
            elif latest_date == current_date:
                profile.chain_length = 1
            else:
                profile.chain_length = 0
            profile.last_chain_date = current_date
            profile.save()

    # 🧠 Simulate quiz activity for 70% of users, once per day max
    active_profiles = random.sample(all_profiles, k=int(0.7 * len(all_profiles))) if all_profiles else []
    eligible_profiles = [
        profile for profile in active_profiles
        if not QuizAttempt.objects.filter(user=profile.user, date_taken__date=current_date).exists()
    ]

    simulate_cmd = SimulateQuizCommand()
    for profile in eligible_profiles:
        num_attempts_today = random.randint(1, 20)
        simulate_cmd.handle_for_profile(profile, num_attempts_today, num_attempts_today, num_questions=10, timestamp=now_time)

    print(f"✅ Simulated {len(eligible_profiles)} active users at {now_time.strftime('%Y-%m-%d %H:%M')}.")
