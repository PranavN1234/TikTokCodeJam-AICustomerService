import threading

class AudioData:
    _instance = None
    data = {}
    event = threading.Event()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioData, cls).__new__(cls)
        return cls._instance

    def set_data(self, key, value):
        self.data[key] = value
        if key == 'transcribed_text':
            self.event.set()  # Signal the event when transcribed_text is updated

    def get_data(self, key):
        return self.data.get(key)

    def clear_data(self):
        self.data = {}
        self.event.clear()  # Clear the event when data is cleared

    def wait_for_response(self, timeout=None):
        self.event.clear()  # Ensure the event is cleared before waiting
        return self.event.wait(timeout)  # Wait for the event to be set

    def is_response_expected(self):
        return self.event.is_set()
