class UserData:
    _instance = None
    data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserData, cls).__new__(cls)
        return cls._instance

    def set_data(self, key, value):
        self.data[key] = value

    def get_data(self, key):
        return self.data.get(key)

    def clear_data(self):
        self.data = {}

    def all_data(self):
        return self.data
