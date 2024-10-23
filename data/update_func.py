import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


# TODO do it later
def update_market_data():
    # local import to avoid circular dependency
    from data.fetch_data import fetch_market_data
    fetch_market_data()


def update_global_data():
    # local import to avoid circular dependency
    from data.fetch_data import fetch_global_data
    fetch_global_data()


def update_trending_data():
    # local import to avoid circular dependency
    from data.fetch_data import fetch_trending_data
    fetch_trending_data()


def update_category_data():
    # local import to avoid circular dependency
    from data.fetch_data import fetch_category_data
    fetch_category_data()


def update_market_dominance():
    # local import to avoid circular dependency
    from data.fetch_data import fetch_market_dominance
    fetch_market_dominance()


def start_scheduler():
    scheduler = BackgroundScheduler()

    # Set up individual schedules for each table update function
    scheduler.add_job(
        update_market_data,
        trigger=IntervalTrigger(minutes=240),
        id="update_market_data",
        name="Updates market data every 240 minutes",
        replace_existing=True
    )

    scheduler.add_job(
        update_global_data,
        trigger=IntervalTrigger(minutes=240),
        id="update_global_data",
        name="Updates global data every 240 minutes",
        replace_existing=True
    )

    scheduler.add_job(
        update_trending_data,
        trigger=IntervalTrigger(minutes=240),
        id="update_trending_data",
        name="Updates trending coins data every 240 minutes",
        replace_existing=True
    )

    scheduler.add_job(
        update_category_data,
        trigger=IntervalTrigger(minutes=240),
        id="update_category_data",
        name="Updates category data every 240 minutes",
        replace_existing=True
    )

    scheduler.add_job(
        update_market_dominance,
        trigger=IntervalTrigger(minutes=240),
        id="update_market_dominance",
        name="Updates market dominance data every 240 minutes",
        replace_existing=True
    )

    # start the scheduler
    scheduler.start()
    print("Scheduler started. Tables will be updated every 240 minutes.")
    # keep the scheduler running
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler shutdown.")
