class FixedCycleController:
    def __init__(self, ns_duration=30, ew_duration=30):
        self.ns_duration = ns_duration
        self.ew_duration = ew_duration
        self.timer = 0
        self.state = 'NS'
        
    def update(self, dt, queues=None):
        self.timer += dt
        if self.state == 'NS' and self.timer >= self.ns_duration:
            self.state = 'EW'
            self.timer = 0
        elif self.state == 'EW' and self.timer >= self.ew_duration:
            self.state = 'NS'
            self.timer = 0
        return self.state
    
    def reset(self):
        self.timer = 0
        self.state = 'NS'
