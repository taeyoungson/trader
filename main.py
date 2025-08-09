import time

from core.scheduler import instance
from trading import jobs


def main():
    instance.DefaultBackgroundScheduler.start()
    jobs.register_jobs()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        instance.DefaultBackgroundScheduler.shutdown()
        print("Scheduler shutdown")


if __name__ == "__main__":
    main()
