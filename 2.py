import pandas as pd
import itertools
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create data for fabric roll A
data_a = {
    'FROM MTR': [7, 15, 23, 25, 28, 30, 41, 41, 52, 66, 68, 71, 76],
    'TO MTR': [7, 15, 23, 25, 28, 30, 41, 41, 52, 66, 68, 71, 76],
    'DEFECT NAME': ['HOLE', 'MISSING END', 'MISSING END', 'RUST STAIN', 'HANDLING STAIN', 'LOOSE WARP', 'MISSING END', 'SLUB', 'RUST STAIN', 'HANDLING STAIN', 'HANDLING STAIN', 'MISSING END', 'WRONG END'],
    'DEFECT TYPE': ['MAJOR', 'MINOR', 'MAJOR', 'MINOR', 'MINOR', 'MINOR', 'MINOR', 'MAJOR', 'MINOR', 'MAJOR', 'MAJOR', 'MINOR', 'MAJOR'],
    'POINTS': [4, 1, 5, 1, 4, 1, 4, 4, 1, 4, 4, 1, 4]
}

# Create updated data for fabric roll B
data_b = {
    'FROM MTR': [4, 10, 14, 16, 37, 41, 47, 59],
    'TO MTR': [8, 10, 14, 16, 37, 41, 47, 59],
    'DEFECT NAME': ['MISSING END', 'RUST STAIN', 'SLUB YARN', 'SLUB YARN', 'RUST STAIN', 'CONTOMINATION', 'CONTOMINATION', 'FLOAT'],
    'DEFECT TYPE': ['MINOR', 'MINOR', 'MAJOR', 'MAJOR', 'MINOR', 'MAJOR', 'MAJOR', 'MAJOR'],
    'POINTS': [1, 1, 4, 4, 1, 4, 4, 1]
}

# Create DataFrames
fabric_a = pd.DataFrame(data_a)
fabric_b = pd.DataFrame(data_b)

# Function to calculate defect point density
def calculate_defect_point_density(segment):
    length = segment['TO MTR'] - segment['FROM MTR'] + 1
    return segment['POINTS'] / length

# Function to remove high defect density segments
def remove_high_defect_segments(fabric, threshold_density):
    return fabric[calculate_defect_point_density(fabric) <= threshold_density]

# Function to calculate total length and defect points for a combination of segments
def calculate_combination_stats(segments):
    total_length = 0
    total_defect_points = 0
    for segment in segments:
        length = segment['TO MTR'] - segment['FROM MTR'] + 1
        total_length += length
        total_defect_points += segment['POINTS']
    return total_length, total_defect_points

# Function to generate all possible combinations of segments
def generate_combinations(fabric):
    all_combinations = []
    for r in range(1, len(fabric) + 1):
        combinations = itertools.combinations(fabric.iterrows(), r)
        for combination in combinations:
            segments = [seg[1] for seg in combination]
            total_length, total_defect_points = calculate_combination_stats(segments)
            all_combinations.append((segments, total_length, total_defect_points))
    return all_combinations

# Function to optimize fabric cuts
def optimize_fabric_cuts(fabric, min_length=20, required_length=80, max_defect_points_per_100m=23):
    all_combinations = generate_combinations(fabric)
    
    valid_combinations = []
    for segments, total_length, total_defect_points in all_combinations:
        if total_length >= min_length and total_length >= required_length:
            defect_points_per_100m = (total_defect_points / total_length) * 100
            if defect_points_per_100m <= max_defect_points_per_100m:
                valid_combinations.append((segments, total_length, total_defect_points, defect_points_per_100m))
    
    valid_combinations.sort(key=lambda x: x[3])  # Sort by defect points per 100 meters
    return valid_combinations

# Define constraints
min_length = 1
required_length = 20
max_defect_points_per_100m = 35

# Remove high defect density segments
threshold_density = 1  # Change this value as needed
filtered_fabric_a = remove_high_defect_segments(fabric_a, threshold_density)
filtered_fabric_b = remove_high_defect_segments(fabric_b, threshold_density)

# Combine filtered data
filtered_fabric_a['Roll'] = 'A'
filtered_fabric_b['Roll'] = 'B'
filtered_fabric = pd.concat([filtered_fabric_a, filtered_fabric_b])

# Find optimal cuts
valid_combinations = optimize_fabric_cuts(filtered_fabric, min_length, required_length, max_defect_points_per_100m)

# Display all valid combinations
print("All possible combinations with total length > 80 meters and defect points within constraints:")
for combination in valid_combinations:
    segments, total_length, total_defect_points, defect_points_per_100m = combination
    print(f"Total Length: {total_length} meters, Total Defect Points: {total_defect_points}, Defect Points per 100 Meters: {defect_points_per_100m:.2f}")
    for segment in segments:
        print(segment)
    print("")

# Plot the best solution (least defect points)
if valid_combinations:
    best_solution = valid_combinations[0]
    segments, total_length, total_defect_points, defect_points_per_100m = best_solution
    
    fig, ax = plt.subplots(figsize=(12, 2))
    y = 0.5  # Single horizontal line
    height = 0.3  # Height of each rectangle
    
    # Plot segments
    for segment in segments:
        roll = segment['Roll']
        start = segment['FROM MTR']
        end = segment['TO MTR']
        ax.add_patch(
            patches.Rectangle((start, y - height / 2), end - start + 1, height, edgecolor='black', facecolor='lightgreen' if roll == 'A' else 'lightblue')
        )
        ax.text((start + end) / 2, y, f"{roll}", ha='center', va='center', color='black')
    
    ax.set_ylim(0, 1)
    ax.set_xlim(0, max(filtered_fabric['TO MTR']))
    ax.set_yticks([y])
    ax.set_yticklabels(['Fabric'])
    ax.set_xlabel('Meters')
    ax.set_title('Optimal Fabric Segments to Cut')
    
    plt.show()
else:
    print("No valid combinations found.")
