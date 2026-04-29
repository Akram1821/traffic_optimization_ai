import numpy as np
from collections import deque

class AdaptiveTrafficController:
    def __init__(self):
        self.action_history = deque(maxlen=10)
        self.threshold = 5
        
    def decide_action(self, queues, current_state, waiting_time):
        """
        Decision logic: prioritize direction with longest queue
        Returns: 'NS' or 'EW'
        """
        ns_queue = len(queues['N']) + len(queues['S'])
        ew_queue = len(queues['E']) + len(queues['W'])
        
        # Smart decision based on queue lengths
        if ns_queue > ew_queue + self.threshold:
            return 'NS'
        elif ew_queue > ns_queue + self.threshold:
            return 'EW'
        else:
            # If queues are similar, alternate but check waiting time
            if waiting_time > 15:  # Long wait detected
                return 'EW' if current_state == 'NS' else 'NS'
            return current_state
    
    def get_state_representation(self, intersection):
        """Extract features for potential ML extension"""
        return {
            'ns_queue': len(intersection.queues['N']) + len(intersection.queues['S']),
            'ew_queue': len(intersection.queues['E']) + len(intersection.queues['W']),
            'total_wait': intersection.total_wait_time,
            'cars_processed': intersection.cars_processed
        }

class RLTrafficController:
    """Simple Q-learning based controller"""
    def __init__(self, learning_rate=0.1, discount=0.95, epsilon=0.1):
        self.q_table = {}
        self.lr = learning_rate
        self.discount = discount
        self.epsilon = epsilon
        
    def get_state_key(self, queues):
        ns = min(len(queues['N']) + len(queues['S']), 10)
        ew = min(len(queues['E']) + len(queues['W']), 10)
        return f"{ns}_{ew}"
    
    def get_action(self, queues, current_state):
        state_key = self.get_state_key(queues)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = {'NS': 0, 'EW': 0}
        
        if np.random.random() < self.epsilon:
            return np.random.choice(['NS', 'EW'])
        else:
            return 'NS' if self.q_table[state_key]['NS'] >= self.q_table[state_key]['EW'] else 'EW'
    
    def update(self, queues, action, reward, next_queues):
        state = self.get_state_key(queues)
        next_state = self.get_state_key(next_queues)
        
        if state not in self.q_table:
            self.q_table[state] = {'NS': 0, 'EW': 0}
        if next_state not in self.q_table:
            self.q_table[next_state] = {'NS': 0, 'EW': 0}
        
        best_next = max(self.q_table[next_state].values())
        self.q_table[state][action] += self.lr * (reward + self.discount * best_next - self.q_table[state][action])
