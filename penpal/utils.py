def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')

    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
        
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    """Calculate Euclidean distance between two RGB colors."""
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

def hex_to_color_name(hex_color):
    # Dictionary of common colors and their hex values
    color_map = {
        'red': '#FF0000',
        'green': '#00FF00',
        'blue': '#0000FF',
        'yellow': '#FFFF00',
        'cyan': '#00FFFF',
        'magenta': '#FF00FF',
        'white': '#FFFFFF',
        'black': '#000000',
        'gray': '#808080',
        'orange': '#FFA500',
        'purple': '#800080',
        'brown': '#A52A2A',
        'pink': '#FFC0CB',
        'lime': '#00FF00',
        'navy': '#000080',
        'teal': '#008080'
    }
    
    # Convert input hex to RGB
    try:
        target_rgb = hex_to_rgb(hex_color)
    except ValueError:
        return 'unknown'
    
    # Find closest color
    min_distance = float('inf')
    closest_color = 'unknown'
    
    for name, hex_value in color_map.items():
        color_rgb = hex_to_rgb(hex_value)
        distance = color_distance(target_rgb, color_rgb)
        
        if distance < min_distance:
            min_distance = distance
            closest_color = name
    
    return closest_color