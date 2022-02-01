import random
import matplotlib.pyplot as plt
import numpy as np


number_count = 10000

# rands = [random.random() for i in range(number_count)]
rands = np.random.normal(size=number_count).tolist()

plt.title(f'Distribution of {number_count} random numbers (sort of normal)')
plt.hist(rands)
plt.show()

samples = 1000
max_samples = 30

means = []
for i in range(samples):
    temp = []
    for j in range(max_samples):
        temp.append(random.choice(rands))
    
    means.append(sum(temp)/len(temp))

plt.hist(means)
plt.title(f"Distribution of the means of {samples} random samples:")
plt.show()

print("test")
print("Test2")