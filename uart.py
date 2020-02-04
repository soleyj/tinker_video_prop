import serial
import ASUS.GPIO as GPIO
import time
ser = serial.Serial("/dev/ttyS1", 9600, timeout=1)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.ASUS)
GPIO.setup(224, GPIO.OUT)
GPIO.output(224, GPIO.LOW)
data_uart=[0,0,0,0,0,0]
uart_coutner = 0



try:
    while 1:
        response = ser.read()
        response = int.from_bytes(response, byteorder='big', signed=False)
        if(response == 240 and uart_coutner == 0):
            uart_coutner = 1
            data_uart[0] = response
        elif(uart_coutner > 0):
            
            data_uart[uart_coutner] = response
            uart_coutner = uart_coutner + 1
            if(uart_coutner == 6):
                if(data_uart[1]==1):
                    print("send")
                    GPIO.output(224, GPIO.HIGH)
                    frame = bytearray()
                    frame.append(0xA2)
                    frame.append(0x0B)
                    frame.append(0x02)
                    print(frame)
                    ser.write(frame)
                    ser.flush()
                uart_coutner = 0
                print(data_uart)
                GPIO.output(224, GPIO.LOW)

            
except KeyboardInterrupt:
    ser.close()