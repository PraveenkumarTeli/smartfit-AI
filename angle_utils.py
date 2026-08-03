from math import atan2,degrees
def calculate_angle(a,b,c):
	angle=degrees(atan2(c.y-b.y,c.x-b.x)-atan2(a.y-b.y,a.x-b.x))
	angle=abs(angle)
	if angle>180:
		angle=360-angle
	return angle
