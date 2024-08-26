from DCMotor import DCMotor
import sys

motor = DCMotor(22)

if(len(sys.argv) < 2 or len(sys.argv) > 2):
    print("Please enter an integer argument")
    exit(0)

t = int(sys.argv[1])

motor.forward(t)

