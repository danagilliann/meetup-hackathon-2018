class Availability:
    def __init__(self):
        self.availability_dict = {}

    def set_dict(self):
        for i in range(0, 24):
            self.availability_dict[i] = ()
            self.availability_dict[(i + .5)] = ()
