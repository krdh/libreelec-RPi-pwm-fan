## PWM (3-pin/4-pin) fan control for LibrELEC on RaspberryPi

```
Based on work from :
    -> Edoardo Paolo Scalafiotti <edoardo849@gmail.com>
    -> Gary Beldon
    -> Miroslav Kuhajda

Tested ( by me ) only:
    -> on RaspberryPi 4 with LibreELEC v11.0.1
    -> with Noktua 5Volt PWM fan
```
## Minimal requirements
```
Script needs at least LibreELEC addons:
    -> rpi-tools ( or raspberry-pi-tools )
    -> python
```

## Installation of script

```bash
### make bin/ directory on permanent storage
mkdir /storage/bin/
### create script ( open file and paste script "pifanpwm.py" in it )
vi /storage/bin/pifanpwm.py
### make script executable
chmod 755 /storage/bin/pifanpwm.py
```

## Simple configuration ( no need to edit script if you don't want change some value )

```python
### Some basic configuration.
FAN_PIN   = 8     ### RaspberryPi GPIO PI used to drive PWM pin of FAN
WAIT_TIME = 15    ### [s] Time to wait between each refresh ( loop turn )
FAN_MIN   = 0     ### [%] Fan minimum speed.
PWM_FREQ  = 25000 ### [Hz] Change this value if fan has strange behavior

### Configurabled temperature to fan speed.
### Raspberry Pi is designed to maximum CPU temperature 85°C so FAN maximum spin is set to 85°C.
###
###          < 20°C =>   0% PWM FAN speed ( FAN stops - no noise )
###     20°C - 29°C =>   0% PWM FAN speed ( FAN stops - no noise )
###     30°C - 39°C =>   0% PWM FAN speed ( FAN stops - no noise )
###     40°C - 49°C =>  25% PWM FAN speed ( FAN spins at 1/4 throttle )
###     50°C - 59°C =>  50% PWM FAN speed ( FAN spins at 1/2 throttle )
###     60°C - 69°C =>  75% PWM FAN speed ( FAN spins at 3/4 throttle )
###     70°C - 79°C => 100% PWM FAN speed ( FAN spins at full throttle )
###          > 80°C => 100% PWM FAN speed ( FAN spins at full throttle )
###
tempSteps  = [20, 30, 40, 50, 60, 70,  80]  ### [°C]
speedSteps = [0,  0,  0,  25, 50, 75, 100]  ### [%]
```

## Basic autostart script at boot ( no restart if script fails )

```bash
### create autostart script ( if does not exists )
echo -e "#!/usr/bin/env bash\n/usr/bin/python /storage/bin/pifanpwm.py &" > "/storage/.config/autostart.sh"
### make script executable
chmod 755 /storage/.config/autostart.sh
```

## Advanced autostart script at boot via systemd service ( with automatic restart if script fails )

```bash
### create systemd service
echo '[Unit]
Description=Fan PWM Service

[Service]
Type=simple
ExecStart=/usr/bin/python /storage/bin/pifanpwm.py
StandardOutput=journal
StandardError=journal
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target' > "/storage/.config/system.d/pifanpwm.service"

### reload systemd configs
systemctl daemon-reload

### enable pifanpwm autostart
systemctl enable pifanpwm.service

### restart pifanpwm autostart
systemctl restart pifanpwm.service

### show status of pifanpwm
systemctl status pifanpwm.service

### print script logs in "less" mode ( last line of the log at the top of screen )
journalctl -u pifanpwm.service
### print script logs in "tail" mode ( same as tail -f )
journalctl -u pifanpwm.service -f
### print script logs in "less" mode in reverse ( last line of the log at the bottom of screen )
journalctl -u pifanpwm.service -r
### print raw log from script - no journalctl stuff ( eg. journalctl datetime, pid, name, etc. )
journalctl -u pifanpwm.service -o cat

### WARNING
###   -> logs are not shown by journalctl in real time
###   -> only changes in fanSpeed are send to log
```

## Testing script

```bash
### to warmup CPU ( stress test )
bash -c "for i in $(echo $(seq 1 1 50)); do nice -n 20 openssl speed &>/dev/null & done"

### to cooldown CPU
killall openssl

### to show temperature
vcgencmd measure_temp

### or autorefresh stats
while true; do
    clear; \
    cat /proc/loadavg | awk '{ print " 1m CPU load: "$1"\n 5m CPU load: "$2"\n15m CPU load: "$3 }'; \
    echo "CPU temp    : $(vcgencmd measure_temp | awk -F '=' '{ print $2 }')"; \
    echo "Free memory : $(free -wm | grep '^Mem' | awk '{ print $4 }') mb"; \
    sleep 5;
done
```
