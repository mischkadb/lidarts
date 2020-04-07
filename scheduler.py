from lidarts import create_app
from redis import Redis
from datetime import datetime
from rq_scheduler import Scheduler

app = create_app()
app.app_context().push()

def register_scheduler():
    scheduler = Scheduler('lidarts-bulk', connection=app.redis)
    list_of_job_instances = scheduler.get_jobs()
    for job in list_of_job_instances:
        scheduler.cancel(job)
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func='lidarts.tasks.bulk_update_last_seen',
        interval=5,
        repeat=None,
        ttl=10,
    )


if __name__ == '__main__':
    register_scheduler()
