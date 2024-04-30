'''
Code redo for the BMS Screen
Updated 4.30.24

Mason Myre

Update notes----
Should be fast enough now
Either that or it doesn't work at all
So basically it's your average Hyundai
huh the sun is coming up

'''
#imports
import board
import busio
import math #not going to use this
import struct #for packing the messages
import time #for waiting a little bit
import analogio
import digitalio
import displayio #for displaying to the screen
import terminalio
import adafruit_ssd1325 #the screen we are using
from adafruit_mcp2515       import MCP2515 as CAN #can stuff
from adafruit_mcp2515.canio import RemoteTransmissionRequest, Message, Match, Timer
from adafruit_display_text import label
import adafruit_mcp2515
import microcontroller 

#variable declarations
current = -1
lowTemp = 20
highTemp = 20
avgTemp = 20
highVolt = 0
lowVolt = 0
amps = 0
voltage = 0

#stuff to help with displaying to screens
cur_text = "A:{:04.1f}".format(current)
volt_text = "V:{:04.1f}".format(voltage)
hlVolt_text = "LV: \n{:01.2f}\nHV: \n{:1.2f}".format(lowVolt, highVolt)
temp_text = "HT: {:04.1f} LT: {:4.1f}".format(highTemp,lowTemp)



#release displays and start the clock
boot_time = time.monotonic()
displayio.release_displays()


#create SPI bus
spi = busio.SPI(board.GP2, board.GP3, board.GP4)

#setup MCP2515 on the SPI bus (CANbus stuff)
can_cs = digitalio.DigitalInOut(board.GP9)
can_cs.switch_to_output()
mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000, silent = False,loopback = False)

#OLED Setup on the SPI bus
cs = board.GP22
dc = board.GP23
reset = board.GP21
WIDTH = 128 #declare it here so we don't have to worry about it later
HEIGHT = 64
BORDER = 0
FONTSCALE = 1
#moar display stuffffff
display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=reset, baudrate=1000000)
display = adafruit_ssd1325.SSD1325(display_bus, width=WIDTH, height=HEIGHT)
display.brightness = 1.0

startTime = time.time() #grab the current time

#display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] =0x000000  # Black

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

#draw the text label on startup
text = "SOLAR CAR ISU\nBMS SCREEN" #nice to know especially for testing
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_width = text_area.bounding_box[2] * FONTSCALE
text_group = displayio.Group(
    scale=FONTSCALE,
    x=display.width // 2 - text_width // 2,
    y=display.height // 2,
)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)
time.sleep(2.5)
splash.pop(-1)

#draw amps label for the first time
text = "A: {:04.1f}".format(current) #creating a string using format to display the information in desired format
text_group = displayio.Group(scale = 2, x = 3; y = 10) #scale 2 because we want it to be kinda big, x and y are spacing
text_area = label.Label(terminalio.FONT, text = text, color = 0xFFFFFF) #define text modifiers
text_group.append(text_area) #subgroup for text scaling 
splash.append(text_group) #add it to be used later


#draw battery pack voltage label for the first time
text = "V: {:04.1f}".format(voltage)
text_group = displayio.Group(scale = 2, x = 3, y = 35)
text_area = label.Label(terminalio.FONT, text = text, color = 0xFFFFFF)
text_group.append(text_area)
splash.append(text_group)


#draw low voltage and high voltage for the first time
text = "LV: \n{:04.1f}\nHV: \n{:4.1f}".format(lowVolt, highVolt)
text_group = displayio.Group(scale = 1, x = 100, y = 5)
text_area = label.Label(terminalio.FONT, text = text, color = 0xFFFFFF)
text_group.append(text_area)
splash.append(text_group)


text = "HT: {:04.1f} LT: {:4.1f}".format(highTemp,lowTemp)
text_group = displayio.Group(scale = 1, x = 0, y = 60) #the formatting on this looks kinda bad,
text_area = label.Label(terminalio.FONT, text = text, color = 0xFFFFFF) #it still fits, but I might make some changes to make it look pretty
text_group.append(text_area)
splash.append(text_group)

# now that was a mess, and you might be thinking: 
# "Mason, this looks worse than my IT168 code, are you sure we can't use a function and pass everything into there and it looks nice and simple?"
# I tried and it was slower than a dodge neon trying to get up a mild incline
# I have no clue, I changed nothing except put it into a function
# Possibly function call stack, but given it's currently 5am and I haven't slept, I'm going to stop talking here at risk of sounding insane (too late)

#writes to the screen every time after the first
def write_to_screen(a, b, c, t, sp):
    text_group = displayio.Group(scale=a, x=b, y=c)
    text_area = label.Label(terminalio.FONT, text=t, color=0xFFFFFF) #black
    text_group.append(text_area)
    splash[sp] = text_group

def _can_is_full():
    mcp._unread_message_queue.clear()

def send_error(bool, loc):
    if bool:
        # Draw temp/dcu timeout Label
        text_group = displayio.Group(scale=1, x=15, y=60)
        text = error_dick[loc] 
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-1] = text_group
        time.sleep(0.5)

    else:
        pass

error_dick = {'BMS': "BMS Fault",'pico_temp': "Pico Overheat",'DCU_timeout': "it ain't got no gas in it" }

def draw_bms_error(fail_str):
    if (current >= 70 or current <= -15):
        # Draw BMS Error
        color_bitmap = displayio.Bitmap(display.width, display.height, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # Black
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        splash.append(bg_sprite)
        text_group = displayio.Group(scale=2, x=3, y=12)
        text = "BMS Fault\n" + fail_str
        text_area = label.Label(terminalio.FONT, text=text, color=0x000000)
        text_group.append(text_area)  # Subgroup for text scaling
        splash.append(text_group)
        #print("BMS Fault:") #for help with testing
        #print(current)
        while True: #what does this do? nothing, we simply do nothing until the car is manually rebooted
            pass #pretty neat, huh?


runtime = time.time()

#our loop that runs while the car is running
while True:
    
    #set up listener
    with mcp.listen(timeout=0) as listener:

        #grab the number of messages we are waiting to receive
        message_count = listener.in_waiting() 
        if message_count > 300: #if unread messages is larger than 300
            _can_is_full() #clear the queue

        #print stuff out here

        #write amperage data to the screen
        text_group = displayio.Group(scale = 2, x = 3, y = 10)
        text_area = label.Label(terminalio.FONT, text = cur_text, color = 0xFFFFFF)
        text_group = append(text_area)
        splash[-4] = text_group

        
        #write pack voltage to the screen
        text_group = displayio.Group(scale = 2, x = 3, y = 35)
        text_area = label.Label(terminalio.FONT, text = volt_text, color = 0xFFFFFF)
        text_group = append(text_area)
        splash[-3] = text_group
        #when other people speak multiple languages they're "a prodigy" or a "polyglot"
        #when I do it, it's called "the bare minimum for comp sci majors"
        #smh double standards


        #write the high/low voltage information to the screen
        text_group = displayio.Group(scale = 1, x = 100, y = 5)
        text_area = label.Label(terminalio.FONT, text = hlVolt_text, color = 0xFFFFFF)
        text_group = append(text_area)
        splash[-2] = text_group

        #write temperature data to the screen
        text_group = displayio.Group(scale = 1, x = 0, y = 60)
        text_area = label.Label(terminalio.FONT, text = temp_text, color = 0xFFFFFF)
        text_group = append(text_area)
        splash[-1] = text_group


        
        next_message = listener.receive() #grab the next message
        message_num = 0 #set a counter for how many messages are in the queue

        while not next_message is None: #aka while we have another message to read
            message_num += 1 #increase the queue counter

            #if we are getting current/voltage data
            if next_message.id == 0x6B0:
                holder = struct.unpack('<hhhh', next_message.data)
                current = holder[1] * .1
                voltage = holder[3] * .1
                #print("Message From: {}: [Amps = {}; Volts = {}]".format(hex(next_message.id),current,voltage))
                cur_text = "A:{:04.1f}".format(current)#do the string building here in case we want to create a little warning for certain values
                volt_text = "V:{:04.1f}".format(voltage) #like if voltage is getting too low or something



            #if we are getting battery temp data
            if next_message.id == 0x6B1:
                #unpack and print the message
                holder = struct.unpack('<hhhxx',next_message.data)
                lowTemp = holder[0] 
                highTemp = holder[1]
                #print("Message From: {}: [Low Temp = {}; High Temp = {}]".format(hex(next_message.id),lowTemp,highTemp))
                temp_text = "HT: {:04.1f} LT: {:4.1f}".format(highTemp,lowTemp) 


            #if we are getting voltage data
            if next_message.id == 0x6B2:
                holder = struct.unpack('<hhhbb',next_message.data)
                highVolt = holder[0] * .001
                lowVolt = holder[1] * .001
                #print("Message From: {}: [Low Volt = {}; High Volt = {}]".format(hex(next_message.id), lowVolt, highVolt))
                hlVolt_text = "LV: \n{:01.2f}\nHV: \n{:1.2f}".format(lowVolt, highVolt)


            if next_message.id == 0x401:
                DCU_timeout = time.monotonic_ns() - prevDCU_time
                prevDCU_time = time.monotonic_ns()
            
            next_message = listener.receive()
            
            #hi
