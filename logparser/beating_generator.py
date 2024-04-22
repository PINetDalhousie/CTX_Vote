import numpy as np
import matplotlib.pyplot as plt

# Function to generate the beating pattern
def beating_pattern(t, fc1, fc2):
    signal1 = np.cos(2 * np.pi * fc1 * t)
    signal2 = np.cos(2 * np.pi * fc2 * t)
    return signal1 + signal2

# Generate time values
t_values = np.linspace(0, 1, 1000)

# Set carrier frequencies for beating
fc1 = 87.8  # Set your desired values for fc1 and fc2
fc2 = 86.5

# Generate the beating pattern
beating_values = beating_pattern(t_values, fc1, fc2)

# Plot the results
plt.figure(figsize=(10, 5))
plt.plot(t_values, beating_values, label=r'$\cos(2\pi f_{c1}t) + \cos(2\pi f_{c2}t)$', color='blue')
plt.title('Graph of the Beating Pattern')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.show()
