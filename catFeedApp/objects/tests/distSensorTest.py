import distanceSensor

sens = distanceSensor.DistanceSensor()

sens.setup()

reading = sens._read_distance_mm()
print("Reading: " + reading + "mm")
avg = sens.getReading_mm(3)
print("3 sample average: " + avg + "mm")



