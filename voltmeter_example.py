from machine import Pin, ADC, Timer, disable_irq, enable_irq
import utime
import display7seg
from time import sleep_ms

#Raspberry Pi PICO (4 digitos)
display_pins = (17, 16, 6, 8, 9, 18, 5) #(a, b, c, d, e, f, g)
transistor_pins = (13, 12, 11)

#Display Object
display7 = display7seg.Display(display_pins,transistor_pins = transistor_pins)

#ADC
adc = ADC(Pin(26))
adc_val = 0

#Counter variable
counter = 0

#Button press variables
button_pin17 = Pin(20, Pin.IN, Pin.PULL_UP)
button_pressed = False
press_counter = 0

#Button pressed routine
def button_pressed_isr(pin):
    state = disable_irq()
    global button_pin
    global button_pressed
    global press_counter #global keyword necesaria para declarar la variable como global, no basta con tenerla en el header
    
    button_pressed = True
    button_pin = pin
    press_counter = press_counter + 1
    enable_irq(state)

#Interrupt Request
button_pin17.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed_isr)

#Read voltage from ADC routine
def read_voltage():
    global adc_val
    adc_val = adc.read_u16()

#Write voltage in 7 segment display routine
def write_voltage():
    voltage = int(round(5*adc_val / 49647.7272, 2)*100)
    display7.show(voltage)

#read_voltage() timer
read_voltage_timer = Timer()
read_voltage_timer.init(period=50, mode=Timer.PERIODIC, callback=lambda t:read_voltage())

#write_voltage() timer
write_voltage_timer = Timer()
write_voltage_timer.init(period=10, mode=Timer.PERIODIC, callback=lambda t:write_voltage())

#Timer init
timer_init = True


while True:
    #Checks if button is pressed and adds to counter
    if button_pressed == True:
        button_pressed = False
        counter += 1
        print(counter)
    
    if (counter % 2) == 1:
        read_voltage_timer.deinit()
        write_voltage_timer.deinit()
        timer_init = False
    
    if (counter % 2) == 1 and timer_init == False:
        read_voltage_timer.init(period=50, mode=Timer.PERIODIC, callback=lambda t:read_voltage())
        write_voltage_timer.init(period=10, mode=Timer.PERIODIC, callback=lambda t:write_voltage())
    