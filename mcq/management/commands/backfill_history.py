from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta, datetime
from mcq.scheduled_jobs.simulate_backfill_step import simulate_backfill_step
import time

class Command(BaseCommand):
    help = "Backfills historical growth and activity for N days."

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='How many past days to simulate.')

    def handle(self, *args, **options):
        days = options['days']
        start_date = now().date() - timedelta(days=days)
        total_cycles = days
        times = []

        self.stdout.write(self.style.NOTICE(f"📅 Backfilling {days} days...\n"))

        for i, day_offset in enumerate(range(days)):
            dt = datetime.combine(start_date + timedelta(days=day_offset), datetime.min.time()).replace(hour=17)
            self.stdout.write(f"⏳ Simulating {dt.strftime('%Y-%m-%d %H:%M')}...")

            start = time.time()
            simulate_backfill_step(dt)
            end = time.time()

            elapsed = end - start
            times.append(elapsed)
            avg = sum(times) / len(times)
            remaining = avg * (total_cycles - (i + 1))
            mins, secs = divmod(int(remaining), 60)

            self.stdout.write(
                f"🕒 Progress: {i + 1}/{total_cycles} | ⏳ Est. time left: {mins}m {secs}s\n"
            )

        self.stdout.write(self.style.SUCCESS(f"\n✅ Finished backfilling {days} days."))
