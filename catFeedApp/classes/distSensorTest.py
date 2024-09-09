import distanceSensor

sens = distanceSensor.DistanceSensor()

sens.setup()

distance = sens._read_distance_mm()

print(distance)
if distance < 0:
    print("Error")
percentfull = round((100-(distance*100/155)),0)

print(str(percentfull) + "% full")

