# PIR_sensor_stability
check PIR stability by connecting it to raspberry pi

put the pir against the wall, or in a box, and run this with 

nohup python3 pir_stability.py >& log &
  
this will put pir vss in high z, then with 0v, and check for false alarm. the high z might not be that good and you still will have 1.5v at the pir vcc vss

at the output you will be able to see how much time it takes for the reset to be stable

connect PIR vcc to 5v, PIR vss to 2, and trigger to port 3. (note that ports 2 and 3 has pull up so don’t switch to them)

note that PIR need 5v. can work a while with 3.3v but with false alarm about once a day 

connect led vcc to 4 and vss to gnd


you can parse the log by 

cat log |grep hash_format|grep -o "{'.*"

cat log |grep -Po 'seconds_from_reset[^,]*'|sort -n -k2 -t:
