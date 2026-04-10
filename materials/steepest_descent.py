from numpy.random import normal
from numpy import zeros, array, dot
from numpy.linalg import norm
from matplotlib.pyplot import plot, show, grid, title
import numdifftools as nd

# DATA GENERATION PART
def fun(x):
    #data generation for fit
    return  0.2*x**2 + 0.5*x + 2 + normal(loc = 0, scale = 0.02, size = size)

size = (50,1) #Nr. observations
xdata = normal(loc = 3, scale = 0.25, size = size)
ydata = fun(xdata)

#OPTIMIZATION PART
def loss(par):
    return 0.5*norm(ydata - (par[0]*xdata**2 + par[1]*xdata + par[2]))**2
    #Norm has a square root threfore the square

#Find the gradient
grad = nd.Gradient(loss)

x = array([0.8,-0.5,5]) #Initial point
grad_at_x = grad(x)
counter = 0 #iter counter
max_iter = 200 #max nr of iterations

toler = 1e-6 #Stop if grad norm less than toler
#flag = 0 grad less than tol, flag = 1 max_iter reached

while True:
    counter += 1
    del_grad = grad(x) - grad_at_x    
    
    #Step size is determined using the Barzilai-Borwein method
    #No checks for division by zero below!
    if counter == 1: #Intial step
        gamma = 0.1
    elif counter % 2 == 0: #alternating long and short steps
        #Long step
        grad_at_x += del_grad
        gamma = dot(del_x, del_x)/dot(del_x, del_grad)        
    elif counter % 2 == 1:
        #Short step
        grad_at_x += del_grad
        gamma = dot(del_x, del_grad)/dot(del_grad, del_grad)
        
    del_x = -gamma*grad_at_x
    x = x + del_x 
#    print("x = ",x) 
    if norm(grad_at_x) < toler:
        flag = 0
        break
    elif counter >= max_iter:
        flag = 1
        break

if flag == 0:
    print("Gradient converged to 0 within tolerance.")
else:
    print("Gradient non-zero")
    
print("x =",x,"\niterations =",counter,"\ngradient =",grad_at_x)

