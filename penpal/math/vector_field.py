import numpy as np
from opensimplex import OpenSimplex

class VectorField:
    def __init__(self, scale=1.0, octaves=3, persistence=0.5, blur_radius=2.0):
        """
        Initialize the vector field generator
        
        Parameters:
        scale: Float, controls the "zoom level" of the noise
        octaves: Int, number of noise layers to combine
        persistence: Float, how much each octave contributes
        blur_radius: Float, amount of smoothing applied
        """
        self.noise_gen1 = OpenSimplex(seed=np.random.randint(1, 1000000))
        self.noise_gen2 = OpenSimplex(seed=np.random.randint(1, 1000000))
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.blur_radius = blur_radius
    
    def _fractal_noise(self, noise_gen, x, y):
        """Generate fractal noise by combining multiple octaves"""
        total = 0
        frequency = 1
        amplitude = 1
        max_value = 0
        
        for _ in range(self.octaves):
            total += noise_gen.noise2(
                x * frequency * self.scale,
                y * frequency * self.scale
            ) * amplitude
            max_value += amplitude
            amplitude *= self.persistence
            frequency *= 2
            
        return total / max_value
    
    def get_vector(self, x, y):
        """
        Get the vector (dx, dy) at position (x, y)
        
        Returns:
        Tuple (dx, dy) representing the direction and magnitude
        """
        # Generate two noise values for x and y components
        dx = self._fractal_noise(self.noise_gen1, x, y)
        dy = self._fractal_noise(self.noise_gen2, x, y)
        
        # Apply gaussian-like blur by sampling neighboring points
        if self.blur_radius > 0:
            samples = 5  # number of blur samples per dimension
            blur_sum_x = 0
            blur_sum_y = 0
            weight_sum = 0
            
            for i in range(-samples//2, samples//2 + 1):
                for j in range(-samples//2, samples//2 + 1):
                    # Calculate sample position and weight
                    sample_x = x + i * self.blur_radius / samples
                    sample_y = y + j * self.blur_radius / samples
                    weight = np.exp(-(i*i + j*j) / (2 * (samples/4)**2))
                    
                    # Add weighted samples
                    blur_sum_x += self._fractal_noise(self.noise_gen1, sample_x, sample_y) * weight
                    blur_sum_y += self._fractal_noise(self.noise_gen2, sample_x, sample_y) * weight
                    weight_sum += weight
            
            dx = blur_sum_x / weight_sum
            dy = blur_sum_y / weight_sum
        
        return (dx, dy)

    def get_normalized_vector(self, x, y):
        """
        Get a normalized vector (dx, dy) at position (x, y)
        
        Returns:
        Tuple (dx, dy) with length 1
        """
        dx, dy = self.get_vector(x, y)
        length = np.sqrt(dx*dx + dy*dy)
        if length > 0:
            return (dx/length, dy/length)
        return (0, 0)