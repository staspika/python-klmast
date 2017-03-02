import numpy as np

i = 3
A = np.zeros((5,5))
A[2][3] = 5
A[3][2] = 4
A[3][3] = 3
B = A.sum(axis=0)
print(A)
print()
i = 2
n = 5
C = A[i:,:]
print("Summen av kolonnene er {}".format(B))
print("Rad {} til {} er:".format(i,n))
print(C)



