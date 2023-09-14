import distanceSensor
from distanceSensor import read_distance

distance = read_distance() * 100

print(distance)

percentfull = round((100-(distance*100/12)),0)

print(percentfull)

if(distance <= 6 or distance > 1000):
    print("Full")
elif(distance > 6 and distance < 10):
    print("about half")
elif(distance >=10 and distance <14):
    print("running low")
elif(distance >=15):
    print("critically low")

