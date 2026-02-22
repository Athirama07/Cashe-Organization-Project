import random

def matrix_multiplication(n=64):
    """Matrix multiplication with good spatial locality"""
    addresses = []
    # Simulate matrix access pattern
    for i in range(n):
        for j in range(n):
            for k in range(n):
                addresses.append(i * n + k)  # Read A
                addresses.append(k * n + j)  # Read B
                addresses.append(i * n + j)  # Write C
    return addresses

def random_access(n=10000, max_addr=100000):
    """Random access pattern"""
    return [random.randint(0, max_addr) for _ in range(n)]

def sequential_access(n=10000):
    """Sequential access pattern"""
    return list(range(n))

def strided_access(n=10000, stride=64):
    """Strided access pattern"""
    return [i * stride % n for i in range(n // stride)]

def linked_list_traversal(n=1000):
    """Simulate linked list with random pointers"""
    next_ptr = list(range(1, n))
    next_ptr.append(0)  # Make it circular
    random.shuffle(next_ptr)
    
    addresses = []
    current = 0
    for _ in range(n * 10):  # Multiple traversals
        addresses.append(current)
        current = next_ptr[current]
    return addresses