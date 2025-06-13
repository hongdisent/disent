import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
import random

class Starfield:
    def __init__(self, width=800, height=800, n_stars=5000, speed=0.01):
        self.width = width
        self.height = height
        self.n_stars = n_stars
        self.speed = speed
        
        # Set random seed for reproducible results
        np.random.seed(42)
        random.seed(42)
        
        # Initialize star positions
        self.reset_stars()
        
        # Set up the plot
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_xlim(-width/2, width/2)
        self.ax.set_ylim(-height/2, height/2)
        self.ax.set_facecolor('black')  # BLACK BACKGROUND
        self.fig.patch.set_facecolor('black')  # Make figure background black too
        self.ax.set_aspect('equal')
        self.ax.axis('off')  # Hide axes for full screen effect
        
        # Store line objects for animation
        self.lines = []
        
    def reset_stars(self):
        """Initialize or reset star positions"""
        # Random positions in 3D space
        self.X = np.random.uniform(-self.width/2, self.width/2, self.n_stars)
        self.Y = np.random.uniform(-self.height/2, self.height/2, self.n_stars)
        self.Z = np.random.uniform(0.1, 1.0, self.n_stars)  # Z > 0 to avoid division by zero
        
    def update_frame(self, frame):
        """Update one frame of the animation"""
        # Clear previous frame with semi-transparent overlay
        self.ax.clear()
        self.ax.set_xlim(-self.width/2, self.width/2)
        self.ax.set_ylim(-self.height/2, self.height/2)
        self.ax.set_facecolor('black')
        self.ax.axis('off')
        
        # Add fade effect by drawing semi-transparent rectangle
        fade_rect = plt.Rectangle((-self.width/2, -self.height/2), 
                                self.width, self.height, 
                                facecolor='black', alpha=0.1, zorder=0)
        self.ax.add_patch(fade_rect)
        
        for i in range(self.n_stars):
            # Calculate current projected position
            x1 = self.X[i] / self.Z[i]
            y1 = self.Y[i] / self.Z[i]
            
            # Move star forward
            self.Z[i] -= self.speed
            
            # Calculate new projected position
            x2 = self.X[i] / self.Z[i]
            y2 = self.Y[i] / self.Z[i]
            
            # Reset star if it's behind the camera
            if self.Z[i] <= 0:
                self.X[i] = np.random.uniform(-self.width/2, self.width/2)
                self.Y[i] = np.random.uniform(-self.height/2, self.height/2)
                self.Z[i] = 1.0
                continue
            
            # Calculate brightness based on Z distance
            # Closer stars (smaller Z) are brighter
            brightness = 1 - self.Z[i]
            brightness = max(0, min(1, brightness))  # Clamp to [0,1]
            
            # Only draw visible stars
            if (abs(x2) < self.width/2 and abs(y2) < self.height/2 and 
                abs(x1) < self.width/2 and abs(y1) < self.height/2):
                
                # Draw streak from old position to new position
                self.ax.plot([x1, x2], [y1, y2], 
                           color='white',        # WHITE STREAKS/DOTS
                           alpha=brightness,
                           linewidth=1.5,
                           solid_capstyle='round')
        
        return []

def create_starfield_animation(width=800, height=800, n_stars=3000, speed=0.008):
    """Create and return the starfield animation"""
    
    starfield = Starfield(width, height, n_stars, speed)
    
    # Create animation
    anim = animation.FuncAnimation(
        starfield.fig, 
        starfield.update_frame,
        frames=None,  # Infinite frames
        interval=50,  # 50ms between frames (~20 FPS)
        blit=False,
        repeat=True,
        cache_frame_data=False  # Don't cache frames to save memory
    )
    
    return starfield.fig, anim

# Alternative implementation using blitting for better performance
class StarfieldOptimized:
    def __init__(self, width=800, height=800, n_stars=5000, speed=0.01):
        self.width = width
        self.height = height
        self.n_stars = n_stars
        self.speed = speed
        
        # Set random seed for reproducible results
        np.random.seed(42)
        
        # Initialize star positions
        self.reset_stars()
        
        # Set up the plot
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_xlim(-width/2, width/2)
        self.ax.set_ylim(-height/2, height/2)
        self.ax.set_facecolor('black')  # BLACK BACKGROUND
        self.fig.patch.set_facecolor('black')  # Make figure background black too
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Pre-create line objects for better performance
        self.lines = []
        for i in range(n_stars):
            line, = self.ax.plot([], [], 'w-', linewidth=1, alpha=0)  # 'w-' = WHITE lines
            self.lines.append(line)
            
        # Background fade overlay
        self.fade_patch = plt.Rectangle((-width/2, -height/2), width, height, 
                                      facecolor='black', alpha=0.05, zorder=-1)
        self.ax.add_patch(self.fade_patch)
        
    def reset_stars(self):
        """Initialize or reset star positions"""
        self.X = np.random.uniform(-self.width/2, self.width/2, self.n_stars)
        self.Y = np.random.uniform(-self.height/2, self.height/2, self.n_stars)
        self.Z = np.random.uniform(0.1, 1.0, self.n_stars)
        
    def update_frame(self, frame):
        """Update one frame of the animation - optimized version"""
        updated_artists = []
        
        for i in range(self.n_stars):
            # Calculate current projected position
            x1 = self.X[i] / self.Z[i]
            y1 = self.Y[i] / self.Z[i]
            
            # Move star forward
            self.Z[i] -= self.speed
            
            # Calculate new projected position
            x2 = self.X[i] / self.Z[i]
            y2 = self.Y[i] / self.Z[i]
            
            # Reset star if it's behind the camera
            if self.Z[i] <= 0:
                self.X[i] = np.random.uniform(-self.width/2, self.width/2)
                self.Y[i] = np.random.uniform(-self.height/2, self.height/2)
                self.Z[i] = 1.0
                self.lines[i].set_data([], [])
                self.lines[i].set_alpha(0)
                updated_artists.append(self.lines[i])
                continue
            
            # Calculate brightness
            brightness = 1 - self.Z[i]
            brightness = max(0, min(1, brightness))
            
            # Check if star is visible
            if (abs(x2) < self.width/2 and abs(y2) < self.height/2 and 
                abs(x1) < self.width/2 and abs(y1) < self.height/2):
                
                # Update line
                self.lines[i].set_data([x1, x2], [y1, y2])
                self.lines[i].set_alpha(brightness)
                self.lines[i].set_linewidth(1 + brightness)  # Thicker lines for brighter stars
            else:
                # Hide invisible stars
                self.lines[i].set_data([], [])
                self.lines[i].set_alpha(0)
            
            updated_artists.append(self.lines[i])
        
        return updated_artists

def create_optimized_starfield(width=800, height=800, n_stars=2000, speed=0.008):
    """Create optimized starfield animation"""
    starfield = StarfieldOptimized(width, height, n_stars, speed)
    
    anim = animation.FuncAnimation(
        starfield.fig,
        starfield.update_frame,
        frames=None,
        interval=30,  # Faster frame rate
        blit=True,    # Use blitting for better performance
        repeat=True,
        cache_frame_data=False
    )
    
    return starfield.fig, anim

# Demo functions
def run_basic_starfield():
    """Run the basic starfield animation"""
    print("Creating 3D Starfield Animation...")
    print("This simulates flying through a field of stars.")
    print("Stars appear as streaks due to motion blur effect.")
    
    fig, anim = create_starfield_animation(
        width=800, 
        height=800, 
        n_stars=2000,  # Reduced for better performance in Jupyter
        speed=0.005    # Adjusted speed
    )
    
    plt.tight_layout()
    return fig, anim

def run_optimized_starfield():
    """Run the optimized starfield animation"""
    print("Creating Optimized 3D Starfield...")
    print("This version uses blitting for better performance.")
    
    fig, anim = create_optimized_starfield(
        width=800,
        height=800,
        n_stars=1500,  # Optimized number
        speed=0.008
    )
    
    plt.tight_layout()
    return fig, anim

# Choose which version to run
print("3D Starfield Animation Options:")
print("1. Basic version - Good for understanding the code")
print("2. Optimized version - Better performance")
print("\nRunning basic version...")

# Create and display the animation
fig, anim = run_basic_starfield()

# Display the animation
plt.show()

# To save the animation (optional):
# anim.save('starfield.gif', writer='pillow', fps=20, dpi=80)
# anim.save('starfield.mp4', writer='ffmpeg', fps=30)

print("\nTo run the optimized version instead, use:")
print("fig, anim = run_optimized_starfield()")
print("plt.show()")