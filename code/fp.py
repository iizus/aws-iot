import sys
import threading
import traceback
from concurrent.futures import Future


class LockedData:
    def __init__(self):
        self.lock: threading.Lock = threading.Lock()
        self.disconnect_called: bool = False


def callback(api: str, future: Future) -> None:
    try:
        future.result() # raises exception if publish failed
        print(f"Published {api} request")
    except Exception as e:
        print(f"Failed to publish {api} request")
        error(e)


# Function for gracefully quitting this sample
def error(msg_or_exception):
    print("Exiting Sample due to exception")
    traceback.print_exception(
        msg_or_exception.__class__,
        msg_or_exception,
        sys.exc_info()[2]
    )