from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import JobLookupError
from datetime import datetime
import atexit

from app.services.automation_service import perform_automation
from app.config import settings

# Create scheduler
scheduler = BackgroundScheduler()

def automation_job():
    """Job to run the automation service"""
    print(f"Running scheduled automation job at {datetime.now().isoformat()}")
    perform_automation()

def init_scheduler():
    """Initialize and start the scheduler"""
    try:
        # Add automation job with cadence from settings
        scheduler.add_job(
            automation_job,
            IntervalTrigger(minutes=settings.AUTOMATION_CADENCE),
            id="automation_job",
            replace_existing=True
        )

        # Start the scheduler
        scheduler.start()
        print(f"Scheduler started. Running every {settings.AUTOMATION_CADENCE} minutes")

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())
    except Exception as e:
        print(f"Error initializing scheduler: {e}")

def modify_job_cadence(minutes: int) -> dict:
    """Modify the cadence of the automation job"""
    try:
        scheduler.remove_job("automation_job")
    except JobLookupError:
        pass

    settings.AUTOMATION_CADENCE = minutes
    scheduler.add_job(
        automation_job,
        IntervalTrigger(minutes=minutes),
        id="automation_job",
        replace_existing=True
    )
    return {"message": f"Job cadence updated to {minutes} minutes"}
