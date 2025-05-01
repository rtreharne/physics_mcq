from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from mcq.scheduled_jobs.simulate_growth import simulate_growth
import time

class Command(BaseCommand):
    help = "Starts the background scheduler for simulating user growth and activity every hour."

    def handle(self, *args, **kwargs):
        interval_minutes = 60

        scheduler = BackgroundScheduler()
        scheduler.add_job(simulate_growth, 'interval', minutes=interval_minutes)
        scheduler.start()

        self.stdout.write(self.style.SUCCESS("📈 Scheduler started — simulating growth every hour."))
        self.stdout.write("⌛ Countdown to next run:")

        try:
            while True:
                for remaining in range(interval_minutes * 60, 0, -1):
                    mins, secs = divmod(remaining, 60)
                    timer = f"{mins:02d}:{secs:02d}"
                    print(f"\r⏳ Next run in {timer}", end="", flush=True)
                    time.sleep(1)
                print("\r✅ Growth simulation triggered! Waiting for next run...\n", end="")
        except (KeyboardInterrupt, SystemExit):
            self.stdout.write("\n🛑 Scheduler stopped.")
            scheduler.shutdown()
