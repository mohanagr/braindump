import numpy as np

n1=10000
m=10000
a=10
s=np.random.randn(n1,m)
x=np.random.randn(n1,m)+a*s
y=np.random.randn(n1,m)+a*s
aa=np.mean(x*y,axis=0)
bb=np.mean(np.sign(x)*np.sign(y),axis=0)
sig_x=np.sqrt((1-np.mean(bb)**2)/n1)
sig_rho=np.pi/2*np.cos(np.pi/2*np.mean(bb))*sig_x
rho=np.sin(bb*np.pi/2)
print(sig_rho, np.std(rho), sig_rho/np.std(rho))
