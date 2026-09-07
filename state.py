class AppState:
    def __init__(self):
        self.city = None
        self.searching_city=None

        # weather api data
        self.globalargs = None
        self.weathertoday = None
        self.forecast = None

        # 3-day forecast
        self.three_dates = []
        self.three_days = []

state = AppState()