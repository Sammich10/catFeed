import distanceSensor

sens = distanceSensor.DistanceSensor()

sens.setup()

distance = sens.read_distance_mm()

print(distance)
if distance < 0:
    print("Error")
percentfull = round((100-(distance*100/150)),0)

print(str(percentfull) + "% full")

