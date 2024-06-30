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

    def add_recent_query(self, query):
        if "recent_queries" not in self.data:
            self.data["recent_queries"] = []
        self.data["recent_queries"].append(query)
        if len(self.data["recent_queries"]) > 3:
            self.data["recent_queries"].pop(0)

    def get_recent_queries(self):
        return self.data.get("recent_queries", [])
    
    def all_data(self):
        return self.data
