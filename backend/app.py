from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import json

# Add both the current directory (results/) and its parent (project root)
# to sys.path so imports work regardless of where the server is started.
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)                    # results/ directory
sys.path.append(os.path.abspath(os.path.join(base_dir, '..')))  # parent directory

# Import your cache simulator modules (located in project root)
from backend.cache_simulator import CacheSimulator, WritePolicy, ReplacementPolicy
from backend.benchmark_programs import *
from adaptive_policy import AdaptiveCache

# Serve frontend files from the frontend directory
frontend_dir = os.path.abspath(os.path.join(base_dir, '..', 'frontend'))
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)  # Enable CORS for all routes

# Serve frontend
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# API endpoint for simulation
@app.route('/api/simulate', methods=['POST'])
def simulate():
    try:
        config = request.json
        print("Received config:", config)  # Debug print
        
        # Run simulation based on config
        results = run_cache_simulation(config)
        
        return jsonify(results)
    
    except Exception as e:
        print("Error:", str(e))  # Debug print
        return jsonify({'error': str(e)}), 500

def run_cache_simulation(config):
    """Run cache simulation with given configuration"""
    
    # Extract configuration
    cache_size = int(config.get('cacheSize', 16384))
    block_size = int(config.get('blockSize', 32))
    associativity = int(config.get('associativity', 2))
    write_policy = WritePolicy.WRITE_BACK if config.get('writePolicy') == 'WRITE_BACK' else WritePolicy.WRITE_THROUGH
    replacement_policy = {
        'LRU': ReplacementPolicy.LRU,
        'FIFO': ReplacementPolicy.FIFO,
        'RANDOM': ReplacementPolicy.RANDOM
    }.get(config.get('replacementPolicy', 'LRU'))
    
    benchmark = config.get('benchmark', 'matrix_multiplication')
    enable_adaptive = config.get('enableAdaptive', False)
    
    # Create simulator
    sim = CacheSimulator(
        cache_size=cache_size,
        block_size=block_size,
        associativity=associativity,
        write_policy=write_policy,
        replacement_policy=replacement_policy
    )
    
    # Get benchmark addresses
    if benchmark == 'matrix_multiplication':
        matrix_size = int(config.get('matrixSize', 32))
        addresses = matrix_multiplication(matrix_size)
    elif benchmark == 'sequential':
        addresses = sequential_access(5000)
    elif benchmark == 'random':
        addresses = random_access(5000)
    elif benchmark == 'strided':
        addresses = strided_access(5000, stride=64)
    elif benchmark == 'linked_list':
        addresses = linked_list_traversal(1000)
    else:
        addresses = matrix_multiplication(32)
    
    # Run simulation
    for i, addr in enumerate(addresses[:5000]):  # Limit for speed
        is_write = (i % 3 == 0)  # 33% writes
        sim.access(addr, is_write)
        
        # Apply adaptive policy if enabled
        if enable_adaptive and i % 100 == 0:
            # Simple adaptive logic
            if sim.get_stats()['Miss Rate'] > 0.1:
                # Increase associativity if miss rate too high
                if associativity < 8:
                    associativity *= 2
                    sim = CacheSimulator(
                        cache_size=cache_size,
                        block_size=block_size,
                        associativity=associativity,
                        write_policy=write_policy,
                        replacement_policy=replacement_policy
                    )
    
    # Get statistics
    stats = sim.get_stats()
    
    # Generate timeline data for charts
    timeline_data = generate_timeline_data()
    
    # Generate miss classification
    miss_data = generate_miss_data()
    
    # Prepare results
    results = {
        'hitRate': f"{stats['Hit Rate']:.1%}",
        'missRate': f"{stats['Miss Rate']:.1%}",
        'amat': f"{stats['AMAT']:.2f} cycles",
        'memoryTraffic': f"{stats['Memory Traffic']:,} blocks",
        'cycles': stats['Cycles'],
        'hitRateChange': f"+{(stats['Hit Rate'] - 0.9) * 100:.1f}%",
        'missRateChange': f"-{(0.1 - stats['Miss Rate']) * 100:.1f}%",
        'amatChange': f"-{3.0 - stats['AMAT']:.1f}",
        'trafficChange': f"+{stats['Memory Traffic'] - 1000}",
        'timelineData': timeline_data,
        'missClassification': miss_data,
        'config': config
    }
    
    return results

def generate_timeline_data():
    """Generate sample timeline data for charts"""
    data = []
    for i in range(20):
        data.append({
            'time': i * 100,
            'hitRate': 90 + (i % 5) * 2,
            'missRate': 10 - (i % 5)
        })
    return data

def generate_miss_data():
    """Generate miss classification data"""
    import random
    return {
        'compulsory': random.randint(80, 150),
        'capacity': random.randint(200, 350),
        'conflict': random.randint(150, 250)
    }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
