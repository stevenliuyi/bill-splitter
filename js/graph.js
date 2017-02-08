import copy

i = 12
n = 5; l = 1; dx = l / float(i); Ta = 20; TB = 100
t = (n * dx) ** 2

a = [-1] * (i-1)
b = [-1] * (i-1)
d = [t+3] + [t+2] * (i-2) + [t+1]
c = [t*Ta+2*TB] + [t*Ta] * (i-1)

T = [100] * i
T_new = [100] * i
epsilon = 1e-5 # error tolerance
k = 0 # number of iterations
error = [] # error for every iteration
while True:
  k += 1
  e = 0
  converge = True
  # update T
  T_new[0] = (c[0] - a[0]*T[1]) / d[0]
  T_new[i-1] = (c[i-1] - b[i-2]*T[i-2]) / d[i-1]
  for j in range(1,i-1):
    T_new[j] = (c[j] - b[j-1]*T[j-1] - a[0]*T[j+1]) / d[j]
  for j in range(0,i):
    if abs(T_new[j]-T[j]) > e: e = abs(T_new[j]-T[j])
  if e > epsilon: converge = False # check for convergence
  error.append(e)
  T = copy.deepcopy(T_new) # update guess
  if converge: break

print k
print error
print T
