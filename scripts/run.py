import asyncio
from bleak import BleakClient
import time
import struct

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


address = "7c:9e:bd:3b:6d:76" # mac address of the arduino

characteristic_UUID = [ "00002a40-0000-1000-8000-00805f9b34fb", "00002a41-0000-1000-8000-00805f9b34fb", "00002a42-0000-1000-8000-00805f9b34fb"]#UUID of each characteristic

values = [ [], [], []]
timestamps = [ [], [], []]
handles = {}
running = True
recording = False
files = [open("datax.csv", "a"), open("datay.csv", "a"), open("dataz.csv", "a")]

# callback called when characteristics value has chenged 
def handle_rx(h: int, data: bytearray):
    global values, timestamps, handles
    val, timestamp = struct.unpack('<fL', data)#extract value and timestamp "float(4)unsigned long(4)" little endian 
    idx = handles[h]# get wich handle is calling the function
    #print("received:",idx, timestamp, val)
    values[idx].append(val)#store the value 
    timestamps[idx].append(timestamp)#store the timestamp
    if(recording):#if recording write the value in the files
        files[idx].write(str(timestamp) + ";"+ str(val) + "\n")

def callback_quit(event):
    global running
    running = False

def callback_rec(event):
    global recording
    recording = not recording
    if(recording):
        print("Recording...")
    else:
        print("Recording stopped.")
# Setup the plot
plt.ion()
fig = plt.figure()
ax = plt.axes(xlim=(0, 10), ylim=(-3,3))
plotcols = ["black","red", "blue"]
lines = []
for index in range(3):
    lobj = ax.plot([],[],lw=1,color=plotcols[index])[0]
    lines.append(lobj)
plt.title("IMU", fontsize=20)
plt.xlabel("timestamp")
plt.ylabel("Acceleration")
plt.xticks(rotation=45, ha='right')
plt.subplots_adjust(bottom=0.30)
ax.set_ylim([-5, 5])

#Setup the buttons
axrec = plt.axes([0.7, 0.05, 0.1, 0.075])
axquit = plt.axes([0.81, 0.05, 0.1, 0.075])
brec = Button(axrec, 'Record')
bquit = Button(axquit, 'Quit')
bquit.on_clicked(callback_quit)
brec.on_clicked(callback_rec)



async def main(address):
    global values, timestamps, handles, running
    async with BleakClient(address) as client:
        s = await client.get_services()# get the services to retrieve the each coresponding handles ids
        for i in range(3):
            handles[s.get_characteristic(characteristic_UUID[i]).handle] = i
            await client.start_notify(characteristic_UUID[i], handle_rx)# start the notify (each time the charact's values changes, the callback is called)
        
        while running:
            await asyncio.sleep(0.001)#pause the coroutine to let so time for the callback 
            for i in range(3):
                values[i] = values[i][-100:]#clip the array 
                timestamps[i] = timestamps[i][-100:]
                lines[i].set_data(timestamps[i], values[i])# update the plot
            ax.set_xlim([timestamps[0][0], timestamps[0][-1]])# restrict to the current timestamps

            fig.canvas.draw()
            fig.canvas.flush_events()


loop = asyncio.run(main(address))

for f in files:#close the files
    f.close()


