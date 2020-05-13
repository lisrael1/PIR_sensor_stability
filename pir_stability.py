#!/usr/bin/python3

# put the pir against the wall, or in a box, and run this with 
# nohup python3 <script>.py >& log &
# this will put pir vss in high z, then with 0v, and check for false alarm. the high z might not be that good and you still will have 1.5v at the pir vcc vss
# at the output you will be able to see how much time it takes for the reset to be stable
# connect PIR vcc to 3.3v or 5v, PIR vss to 2, and trigger to port 3. (note that ports 2 and 3 has pull up so don’t switch to them)
# connect led vcc to 4 and vss to gnd

# you can parse the log by 
# cat log |grep hash_format|grep -o "{'.*"
# cat log |grep -Po 'seconds_from_reset[^,]*'|sort -n -k2 -t:

import RPi.GPIO as GPIO  # pip3 install rpi.gpio
from time import sleep
import numpy as np
from datetime import datetime
import traceback
import functools
print = functools.partial(print, flush=True)

class timer:
    def __init__(self):
        import time
        self.time=time
        self.start = time.time()  # you can also use time.perf_counter() instead, might be more accurate. return float seconds
    def seconds_till_now(self):
        return self.time.time() - self.start
    def __del__(self): pass 
    def __exit__(self, exception_type, exception_value, traceback): pass # needed for using at 'with' command
    def __enter__(self): pass

print('INFO: setting GPIO')
GPIO.setmode(GPIO.BCM)  # setting numbers like at the common chart

global_timer_from_reset=timer()
# port numbers
vss=14
trigger=15

# led ports - optional- you can directly connect the led to ports 9 and 10
led=18

# some setups
check_duration_range=[9,3*60]


GPIO.setup(led, GPIO.OUT)
GPIO.setup(trigger, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
for _ in range(3):
    GPIO.output(led, GPIO.HIGH)
    sleep(0.1)
    GPIO.output(led, GPIO.LOW)
    sleep(0.1)


print('INFO: starting loop')

loop_time_s,reset_time_s=10,2  # setting first loop to be fast one

while True: 
    try:
        GPIO.setup(vss, GPIO.IN)  # i want them to be floating without outputing voltage

        print('INFO: waiting {:>3d} sec for reset'.format(reset_time_s))
        print(''' hash_format: {{'level':'INFO','m_type':'reset_time','value':{}}}'''.format(reset_time_s))
        sleep(reset_time_s)

        GPIO.setup(vss, GPIO.OUT)
        GPIO.output(vss, GPIO.LOW)
        
        timer_from_reset=timer()
        timer_from_last_event=timer()

        loop_is_done=False
        number_of_errors=0
        while loop_is_done==False:
            end_time=int(loop_time_s-timer_from_reset.seconds_till_now())
            if end_time>0:
                print('INFO: waiting for trigger event with timeout of {:>5d} sec'.format(end_time))
                output_code=GPIO.wait_for_edge(trigger,GPIO.RISING,500,end_time*1000)  # bounce time 500ms. at this stage it will not get keyboard interrupt until you will have event and then it will exit the program
                # output_code will be the port number at rising edge or None at timout
            if end_time>0 and output_code is not None:
                print('ERROR: false alarm after {:>5d} sec from reset at port {} at {}'.format(int(timer_from_reset.seconds_till_now()),output_code,datetime.now().strftime("%Y-%m-%d__%H:%M:%S")))
                print(''' hash_format: {{'level':'ERROR','m_type':'false_alarm','seconds_from_reset':{},'seconds_from_last_event':{},'date':'{}'}}'''.format(int(timer_from_reset.seconds_till_now()),int(timer_from_last_event.seconds_till_now()),datetime.now().strftime("%Y-%m-%d__%H:%M:%S")))
                timer_from_last_event=timer()
                number_of_errors+=1
                GPIO.output(led, GPIO.HIGH)
                sleep(1)
                GPIO.output(led, GPIO.LOW)
            else:
                print('INFO: ending loop of {:>5d} sec with {:>5d} errors'.format(loop_time_s,number_of_errors))
                print(''' hash_format: {{'level':'INFO','m_type':'end_loop','errors':{}, 'loop_time_s':{}}}'''.format(number_of_errors, loop_time_s))
                loop_is_done=True
        reset_time_s=np.random.randint(1,60)
        loop_time_s=int(np.random.randint(*check_duration_range)*60)

            
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        print("Keyboard interrupt")
        GPIO.cleanup()
        break
    except:
        print(traceback.format_exc())
        GPIO.cleanup()
        break   
