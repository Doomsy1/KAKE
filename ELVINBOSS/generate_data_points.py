import random   

def generate_data_point():
    """Generate a single data point with random values."""
    # Generate random values
    point_id = random.randint(0, 1)
    int_val1 = random.randint(100, 2000)
    int_val2 = random.randint(100, 2000)
    float_val1 = round(random.uniform(10.0, 200.0), 1)
    float_val2 = round(random.uniform(10.0, 200.0), 1)
    float_val3 = round(random.uniform(10.0, 200.0), 1)
    
    # Format the point
    return f"{point_id}, {int_val1}, {int_val2}, {float_val1}, {float_val2}, {float_val3}"

def generate_data(num_points=1):
    """
    Generate data string with specified number of points (1 or 2).
    Each point contains: [point_id], int_val1, int_val2, [float_val1], [float_val2], [float_val3]
    Points are separated by ' | ' if there are two points.
    """
    if num_points not in [1, 2]:
        raise ValueError("Number of points must be 1 or 2")
    
    points = [generate_data_point() for _ in range(num_points)]
    return " | ".join(points)
