from collections import defaultdict

class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)

    def inc(self, name: str, amount: int = 1):
        self.counters[name] += amount

    def snapshot(self):
        return dict(self.counters)


metrics = Metrics()
