class NullScraper:
    def __init__(self):
        self._rate = 60
        self._step = 3

    def get_rate(self):
        rate = self._rate
        self._rate += self._step
        if self._rate >= 180 or self._rate <= 60:
            self._step = -self._step
        return rate

    def close(self):
        pass
