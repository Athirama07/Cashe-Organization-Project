from backend.cache_simulator import CacheSimulator, WritePolicy, ReplacementPolicy
import numpy as np

class AdaptiveCache:
    def __init__(self, base_config):
        self.config = base_config
        self.miss_rate_history = []
        self.threshold = 0.1  # 10% miss rate threshold
        self.adaptation_interval = 1000
        self.access_count = 0
        self.current_policy = ReplacementPolicy.LRU
        self.best_config = None
        
    def adapt(self, simulator):
        """Monitor and adapt cache configuration"""
        self.access_count += 1
        
        if self.access_count % self.adaptation_interval == 0:
            current_miss_rate = simulator.misses / simulator.accesses
            
            # Store miss rate
            self.miss_rate_history.append(current_miss_rate)
            
            # Check if adaptation needed
            if current_miss_rate > self.threshold:
                self.adapt_policy(simulator)
            
            # Analyze workload pattern
            if len(self.miss_rate_history) > 5:
                workload_type = self.classify_workload()
                self.adapt_config(workload_type)
    
    def adapt_policy(self, simulator):
        """Switch replacement policy based on miss rate"""
        if self.current_policy == ReplacementPolicy.LRU:
            simulator.replacement_policy = ReplacementPolicy.FIFO
            self.current_policy = ReplacementPolicy.FIFO
        else:
            simulator.replacement_policy = ReplacementPolicy.LRU
            self.current_policy = ReplacementPolicy.LRU
    
    def classify_workload(self):
        """Classify workload based on miss rate pattern"""
        recent_rates = self.miss_rate_history[-5:]
        
        if all(r < 0.05 for r in recent_rates):
            return "sequential"
        elif any(r > 0.2 for r in recent_rates):
            if np.std(recent_rates) > 0.1:
                return "random"
            else:
                return "conflict"
        else:
            return "mixed"
    
    def adapt_config(self, workload_type):
        """Adapt configuration based on workload type"""
        if workload_type == "sequential":
            # Increase block size for sequential access
            self.config['block_size'] = min(128, self.config['block_size'] * 2)
        elif workload_type == "random":
            # Decrease block size for random access
            self.config['block_size'] = max(16, self.config['block_size'] // 2)
        elif workload_type == "conflict":
            # Increase associativity for conflict misses
            self.config['associativity'] = min(8, self.config['associativity'] * 2)