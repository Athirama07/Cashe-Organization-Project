import random
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum
import pandas as pd

class WritePolicy(Enum):
    WRITE_THROUGH = 1
    WRITE_BACK = 2

class ReplacementPolicy(Enum):
    LRU = 1
    FIFO = 2
    RANDOM = 3

class CacheLine:
    def __init__(self, block_size):
        self.valid = False
        self.tag = None
        self.data = [0] * block_size
        self.last_access = 0
        self.load_time = 0

class CacheSet:
    def __init__(self, associativity, block_size, replacement_policy):
        self.lines = [CacheLine(block_size) for _ in range(associativity)]
        self.replacement_policy = replacement_policy
        self.access_counter = 0
        self.fifo_queue = list(range(associativity))  # For FIFO
        
    def find_line(self, tag):
        for i, line in enumerate(self.lines):
            if line.valid and line.tag == tag:
                if self.replacement_policy == ReplacementPolicy.LRU:
                    line.last_access = self.access_counter
                return i, line
        return None, None
    
    def get_evict_candidate(self):
        if self.replacement_policy == ReplacementPolicy.RANDOM:
            return random.randint(0, len(self.lines) - 1)
        elif self.replacement_policy == ReplacementPolicy.FIFO:
            candidate = self.fifo_queue[0]
            self.fifo_queue = self.fifo_queue[1:] + [candidate]
            return candidate
        else:  # LRU
            lru_index = 0
            lru_time = self.lines[0].last_access
            for i, line in enumerate(self.lines):
                if line.last_access < lru_time:
                    lru_time = line.last_access
                    lru_index = i
            return lru_index

class CacheSimulator:
    def __init__(self, cache_size=16384, block_size=32, associativity=2,
                 write_policy=WritePolicy.WRITE_BACK,
                 replacement_policy=ReplacementPolicy.LRU,
                 hit_time=1, miss_penalty=10):
        
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.write_policy = write_policy
        self.replacement_policy = replacement_policy
        self.hit_time = hit_time
        self.miss_penalty = miss_penalty
        
        # Calculate number of sets
        self.num_sets = cache_size // (block_size * associativity)
        self.sets = [CacheSet(associativity, block_size, replacement_policy) 
                    for _ in range(self.num_sets)]
        
        # Statistics
        self.accesses = 0
        self.hits = 0
        self.misses = 0
        self.read_accesses = 0
        self.write_accesses = 0
        self.memory_traffic = 0
        self.cycles = 0
        
    def get_set_index(self, address):
        return (address // self.block_size) % self.num_sets
    
    def get_tag(self, address):
        return address // (self.block_size * self.num_sets)
    
    def access(self, address, is_write=False):
        self.accesses += 1
        if is_write:
            self.write_accesses += 1
        else:
            self.read_accesses += 1
            
        set_index = self.get_set_index(address)
        tag = self.get_tag(address)
        
        cache_set = self.sets[set_index]
        cache_set.access_counter += 1
        
        # Check if tag exists in set
        line_index, line = cache_set.find_line(tag)
        
        if line is not None:  # Cache HIT
            self.hits += 1
            self.cycles += self.hit_time
            
            if is_write and self.write_policy == WritePolicy.WRITE_THROUGH:
                self.memory_traffic += 1  # Write to memory
                
        else:  # Cache MISS
            self.misses += 1
            self.cycles += self.miss_penalty
            
            # Find eviction candidate
            evict_index = cache_set.get_evict_candidate()
            
            # Handle write-back if needed
            if self.write_policy == WritePolicy.WRITE_BACK and cache_set.lines[evict_index].valid:
                self.memory_traffic += 1  # Write back to memory
            
            # Load new block
            cache_set.lines[evict_index].valid = True
            cache_set.lines[evict_index].tag = tag
            cache_set.lines[evict_index].last_access = cache_set.access_counter
            cache_set.lines[evict_index].load_time = cache_set.access_counter
            self.memory_traffic += 1  # Read from memory
            
            if is_write and self.write_policy == WritePolicy.WRITE_THROUGH:
                self.memory_traffic += 1  # Additional write to memory
    
    def get_stats(self):
        hit_rate = self.hits / self.accesses if self.accesses > 0 else 0
        miss_rate = self.misses / self.accesses if self.accesses > 0 else 0
        amat = self.hit_time + miss_rate * self.miss_penalty
        
        return {
            'Accesses': self.accesses,
            'Hits': self.hits,
            'Misses': self.misses,
            'Hit Rate': hit_rate,
            'Miss Rate': miss_rate,
            'AMAT': amat,
            'Cycles': self.cycles,
            'Memory Traffic': self.memory_traffic
        }