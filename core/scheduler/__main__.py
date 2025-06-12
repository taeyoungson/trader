import time

from core.scheduler import instance
from trading import database  # noqa: F401
from trading import runners  # noqa: F401


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
