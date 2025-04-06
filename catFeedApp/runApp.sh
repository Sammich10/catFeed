# Load environment variables
. ./createEnvVars.sh

# Check if pigpio service is running
running=$(systemctl is-active pigpiod)

if [ "$running" != "active" ]; then
    echo "pigpiod service is not running. Starting it..."
    sudo systemctl start pigpiod
    if [ $? -ne 0 ]; then
        echo "Failed to start pigpiod service."
        exit 1
    else
        echo "pigpiod service started successfully."
    fi
fi

python3 run.py