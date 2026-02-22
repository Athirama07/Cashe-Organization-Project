import os
from backend.cache_simulator import CacheSimulator, WritePolicy, ReplacementPolicy
from backend.benchmark_programs import *
from adaptive_policy import AdaptiveCache
import pandas as pd
import matplotlib.pyplot as plt

# ensure output directory exists for any results
os.makedirs('results', exist_ok=True)

def main():
    print("=" * 60)
    print("CACHE ORGANIZATION AND POLICY ANALYSIS")
    print("=" * 60)
    
    # Part 1: Basic Cache Organization Comparison
    print("\n[1] Comparing Cache Organizations...")
    organizations = [
        {"name": "Direct-Mapped", "associativity": 1},
        {"name": "2-Way Set Associative", "associativity": 2},
        {"name": "4-Way Set Associative", "associativity": 4},
        {"name": "Fully Associative", "associativity": 8}
    ]
    
    addresses = matrix_multiplication(32)
    org_results = []
    
    for org in organizations:
        sim = CacheSimulator(
            cache_size=16384,
            associativity=org["associativity"]
        )
        
        for addr in addresses[:3000]:
            sim.access(addr)
        
        stats = sim.get_stats()
        org_results.append({
            "Organization": org["name"],
            "Hit Rate": f"{stats['Hit Rate']:.2%}",
            "Miss Rate": f"{stats['Miss Rate']:.2%}",
            "AMAT": f"{stats['AMAT']:.2f} cycles",
            "Cycles": stats['Cycles']
        })
    
    # Display results
    df_org = pd.DataFrame(org_results)
    print("\nCache Organization Comparison:")
    print(df_org.to_string(index=False))
    
    # Part 2: Block Size Impact
    print("\n[2] Analyzing Block Size Impact...")
    block_sizes = [16, 32, 64, 128]
    block_results = []
    
    for bs in block_sizes:
        sim = CacheSimulator(block_size=bs)
        for addr in strided_access(2000, stride=64):
            sim.access(addr)
        stats = sim.get_stats()
        block_results.append({
            "Block Size": f"{bs} bytes",
            "Hit Rate": f"{stats['Hit Rate']:.2%}",
            "Miss Rate": f"{stats['Miss Rate']:.2%}",
            "Memory Traffic": stats['Memory Traffic']
        })
    
    df_block = pd.DataFrame(block_results)
    print(df_block.to_string(index=False))
    
    # Part 3: Replacement Policy Comparison
    print("\n[3] Comparing Replacement Policies...")
    policies = [
        ("LRU", ReplacementPolicy.LRU),
        ("FIFO", ReplacementPolicy.FIFO),
        ("Random", ReplacementPolicy.RANDOM)
    ]
    
    # Test with different access patterns
    patterns = {
        "Sequential": sequential_access(2000),
        "Random": random_access(2000),
        "Strided": strided_access(2000, stride=16)
    }
    
    for pattern_name, pattern_addrs in patterns.items():
        print(f"\n  Workload: {pattern_name}")
        for policy_name, policy in policies:
            sim = CacheSimulator(replacement_policy=policy)
            for addr in pattern_addrs:
                sim.access(addr)
            stats = sim.get_stats()
            print(f"    {policy_name:8} | Hit Rate: {stats['Hit Rate']:.2%} | AMAT: {stats['AMAT']:.2f}")
    
    # Part 4: Write Policy Comparison
    print("\n[4] Comparing Write Policies...")
    write_policies = [
        ("Write-Through", WritePolicy.WRITE_THROUGH),
        ("Write-Back", WritePolicy.WRITE_BACK)
    ]
    
    for wp_name, wp in write_policies:
        sim = CacheSimulator(write_policy=wp)
        for addr in matrix_multiplication(16):
            # Mix reads and writes
            is_write = random.random() > 0.7  # 30% writes
            sim.access(addr, is_write)
        stats = sim.get_stats()
        print(f"  {wp_name:13} | Memory Traffic: {stats['Memory Traffic']} blocks | Cycles: {stats['Cycles']}")
    
    # Part 5: Unique Feature - Adaptive Cache
    print("\n[5] Testing Adaptive Cache (Unique Feature)...")
    config = {
        'cache_size': 16384,
        'block_size': 32,
        'associativity': 2
    }
    adaptive = AdaptiveCache(config)
    
    # Test with varying workload
    print("  Simulating workload with changing patterns...")
    workload = []
    workload.extend(sequential_access(2000))      # Sequential
    workload.extend(random_access(2000))           # Random
    workload.extend(strided_access(2000, 32))      # Strided
    
    sim = CacheSimulator(**config)
    for addr in workload:
        sim.access(addr)
        adaptive.adapt(sim)
    
    stats = sim.get_stats()
    print(f"  Final Hit Rate: {stats['Hit Rate']:.2%}")
    print(f"  AMAT: {stats['AMAT']:.2f} cycles")
    
    print("\n" + "=" * 60)
    print("Analysis Complete! Check results/cache_analysis.png for visualizations")
    print("=" * 60)

if __name__ == "__main__":
    main()