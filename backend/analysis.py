import os
import random
import matplotlib.pyplot as plt
import pandas as pd
from backend.cache_simulator import CacheSimulator, WritePolicy, ReplacementPolicy
from backend.benchmark_programs import *

# make sure results directory exists
os.makedirs('results', exist_ok=True)

def run_comparison():
    results = []
    
    # Test different configurations
    associativity_values = [1, 2, 4, 8]  # 1 = direct-mapped
    block_sizes = [16, 32, 64, 128]
    policies = [ReplacementPolicy.LRU, ReplacementPolicy.FIFO, ReplacementPolicy.RANDOM]
    
    # Run matrix multiplication benchmark
    addresses = matrix_multiplication(32)
    
    for assoc in associativity_values:
        for block_size in block_sizes:
            for policy in policies:
                # Create simulator
                sim = CacheSimulator(
                    cache_size=16384,
                    block_size=block_size,
                    associativity=assoc,
                    replacement_policy=policy
                )
                
                # Run simulation
                for addr in addresses[:5000]:  # Limit for speed
                    sim.access(addr)
                
                # Get statistics
                stats = sim.get_stats()
                stats['Associativity'] = assoc
                stats['Block Size'] = block_size
                stats['Policy'] = policy.name
                results.append(stats)
    
    return pd.DataFrame(results)

def plot_results(df):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Hit Rate vs Associativity
    for assoc in df['Associativity'].unique():
        data = df[df['Associativity'] == assoc]
        axes[0, 0].plot(data['Block Size'], data['Hit Rate'], 
                        marker='o', label=f'{assoc}-way')
    axes[0, 0].set_xlabel('Block Size (bytes)')
    axes[0, 0].set_ylabel('Hit Rate')
    axes[0, 0].set_title('Hit Rate vs Cache Configuration')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Plot 2: AMAT Comparison
    for policy in df['Policy'].unique():
        data = df[df['Policy'] == policy]
        axes[0, 1].plot(data['Associativity'], data['AMAT'], 
                        marker='s', label=policy)
    axes[0, 1].set_xlabel('Associativity')
    axes[0, 1].set_ylabel('AMAT (cycles)')
    axes[0, 1].set_title('AMAT for Different Policies')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # Plot 3: Miss Classification
    workloads = ['Sequential', 'Random', 'Strided']
    miss_rates = []
    for workload in [sequential_access(5000), random_access(5000), 
                     strided_access(5000)]:
        sim = CacheSimulator()
        for addr in workload:
            sim.access(addr)
        miss_rates.append(sim.get_stats()['Miss Rate'])
    
    axes[1, 0].bar(workloads, miss_rates)
    axes[1, 0].set_ylabel('Miss Rate')
    axes[1, 0].set_title('Miss Rate for Different Workloads')
    axes[1, 0].grid(True)
    
    # Plot 4: Memory Traffic
    write_policies = ['Write-Through', 'Write-Back']
    traffic = []
    for policy in [WritePolicy.WRITE_THROUGH, WritePolicy.WRITE_BACK]:
        sim = CacheSimulator(write_policy=policy)
        for addr in matrix_multiplication(16):
            sim.access(addr, is_write=(random.random() > 0.5))
        traffic.append(sim.get_stats()['Memory Traffic'])
    
    axes[1, 1].bar(write_policies, traffic)
    axes[1, 1].set_ylabel('Memory Traffic (blocks)')
    axes[1, 1].set_title('Memory Traffic Comparison')
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('results/cache_analysis.png', dpi=300)
    plt.show()

# Main execution
if __name__ == "__main__":
    print("Running cache simulations...")
    
    # Run comparisons
    results_df = run_comparison()
    
    # Save results
    results_df.to_csv('results/simulation_results.csv', index=False)
    
    # Generate plots
    plot_results(results_df)
    
    print("Analysis complete! Check results/ directory for outputs.")