'''
Code redo for the BMS Screen
pleasework
'''
#importss
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

#draw the text label
text = "SOLAR CAR ISU\nBMS SCREEN\n"
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


#function creation area
#writes to the screen the first time
def init_screen_writing(a, b, c, t):
    text_group = displayio.Group(scale=a, x=b, y=c)
    text_area = label.Label(terminalio.FONT, text=t, color=0xFFFFFF) #black
    text_group.append(text_area)
    splash.append(text_group)

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

#print stuff as we initialize it
text = "A: {:04.1f}".format(current)
init_screen_writing(2, 3, 10, text)

text = "V: {:04.1f}".format(voltage)
init_screen_writing(2, 3, 35, text)

text = "LV: \n{:04.1f}\nHV: \n{:4.1f}".format(lowVolt, highVolt)
init_screen_writing(1, 100, 5, text)

text = "HT: {:04.1f} LT: {:4.1f}".format(highTemp,lowTemp)
init_screen_writing(1, 0, 60, text)


runtime = time.time()

while True:

	with mcp.listen(timeout=0) as listener:

		message_count = listener.in_waiting()
		if message_count > 300:
			_can_is_full()

		next_message = listener.receive()
		message_num = 0

		while not next message is None:
			message_num += 1

			if next_message.id == 0x6B0:
				holder = struct.unpack('<hhhh', next_message.data)
				current = holder[1] * .1
				voltage = holder[3] * .1
                print("Message From: {}: [Amps = {}; Volts = {}]".format(hex(next_message.id),current,voltage))

			if next_message.id == 0x6B1:
                #unpack and print the message
                holder = struct.unpack('<hhhxx',next_message.data)
                lowTemp = holder[0] 
                highTemp = holder[1]
                print("Message From: {}: [Low Temp = {}; High Temp = {}]".format(hex(next_message.id),lowTemp,highTemp))

            if next_message == 0x6B2:
                holder = struct.unpack('<HHHBB',next_message.data)
                highVolt = holder[0] * .0001
                lowVolt = holder[1] * .0001

            if next_message == 0x401:
                DCU_timeout = time.monotonic_ns() - prevDCU_time
                prevDCU_time = time.monotonic_ns()



            next_message = listener.receive()









