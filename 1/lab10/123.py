from pylab import *
# Figure name
figure(1, dpi=300)

# Plotting inclined surface
plot([0,R],[0,-y0],linewidth=5)

# plotting y=0 line
plot([0,R],[0,0],'k',linewidth=1)

# Array of x
x=linspace(0,R,50)

# Evaluating y based on x
y=x*tan(?)-(1/2)*(g*x**2)/(u**2*(cos(?))**2 )

# Plotting projectile
plot(x,y,'r-',linewidth=2)
xlabel('x')
ylabel('y')
savefig("Inc_Proj.jpg")
show()