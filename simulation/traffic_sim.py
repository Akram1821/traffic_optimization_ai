import numpy as np
import random
from collections import deque
import time

class TrafficLight:
    def __init__(self):
        self.state = 'NS'  # NS or EW
        self.timer = 0
        self.cycle_time = 30
    
    def update(self, dt, ai_control=False, ns_waiting=0, ew_waiting=0):
        self.timer += dt
        if not ai_control:
            if self.timer >= self.cycle_time:
                self.state = 'EW' if self.state == 'NS' else 'NS'
                self.timer = 0
        return self.state

class Car:
    def __init__(self, direction, arrival_time):
        self.direction = direction  # 'N', 'S', 'E', 'W'
        self.arrival_time = arrival_time
        self.wait_time = 0
        self.departure_time = None

class Intersection:
    def __init__(self):
        self.queues = {
            'N': deque(),
            'S': deque(),
            'E': deque(),
            'W': deque()
        }
        self.traffic_light = TrafficLight()
        self.time = 0
        self.total_wait_time = 0
        self.cars_processed = 0
        self.history = {'wait_times': [], 'queue_lengths': []}
        
    def generate_car(self, rate=0.5):
        if random.random() < rate * 0.1:
            direction = random.choice(['N', 'S', 'E', 'W'])
            car = Car(direction, self.time)
            self.queues[direction].append(car)
            return True
        return False
    
    def update(self, dt, ai_control=False):
        self.time += dt
        
        # Generate cars
        for _ in range(4):
            self.generate_car()
        
        # Update traffic light
        ns_waiting = len(self.queues['N']) + len(self.queues['S'])
        ew_waiting = len(self.queues['E']) + len(self.queues['W'])
        state = self.traffic_light.update(dt, ai_control, ns_waiting, ew_waiting)
        
        # Process cars
        cars_passed = 0
        if state == 'NS':
            for dir in ['N', 'S']:
                if self.queues[dir] and cars_passed < 2:
                    car = self.queues[dir].popleft()
                    car.departure_time = self.time
                    wait = car.departure_time - car.arrival_time
                    self.total_wait_time += wait
                    self.cars_processed += 1
                    cars_passed += 1
        else:
            for dir in ['E', 'W']:
                if self.queues[dir] and cars_passed < 2:
                    car = self.queues[dir].popleft()
                    car.departure_time = self.time
                    wait = car.departure_time - car.arrival_time
                    self.total_wait_time += wait
                    self.cars_processed += 1
                    cars_passed += 1
        
        # Update wait times for queued cars
        for queue in self.queues.values():
            for car in queue:
                car.wait_time += dt
        
        # Record metrics
        total_queue = sum(len(q) for q in self.queues.values())
        avg_wait = self.total_wait_time / self.cars_processed if self.cars_processed > 0 else 0
        self.history['queue_lengths'].append(total_queue)
        self.history['wait_times'].append(avg_wait)
        
        return {
            'time': self.time,
            'queue_length': total_queue,
            'avg_wait_time': avg_wait,
            'cars_processed': self.cars_processed,
            'light_state': state
        }
    
    def reset(self):
        self.queues = {k: deque() for k in self.queues}
        self.traffic_light = TrafficLight()
        self.time = 0
        self.total_wait_time = 0
        self.cars_processed = 0
        self.history = {'wait_times': [], 'queue_lengths': []}
