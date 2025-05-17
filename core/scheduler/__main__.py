import time

from core.scheduler import instance
from trade import data  # noqa


def main():
    instance.DefaultBackgroundScheduler.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        instance.DefaultBackgroundScheduler.shutdown()
        print("Scheduler shutdown")


if __name__ == "__main__":
    main()
