import numpy as np 

a = np.array([(1,2),(3,4),(12,32),(34, 3)])

a = np.array(np.delete(a, 1), dtype=tuple)
print(a)