#!/usr/bin/python

import time
import datetime
import json
import math

from smbus2 import SMBus

from .publisher import publish_data
from .utils import get_uuids

address = 0x2A

def monitor_loop():
 
    epoch = datetime.datetime(1970,1,1)

    # Get I2C bus
    bus = SMBus(1)

    # PECMAC125A address, 0x2A(42)
    # Command for reading device identification data
    # 0x6A(106), 0x02(2), 0x00(0),0x00(0), 0x00(0) 0x00(0), 0xFE(254)
    # Header byte-2, command-2, byte 3, 4, 5 and 6 are reserved, checksum
    getDeviceCommand = [0x6A, 0x02, 0x00, 0x00, 0x00, 0x00, 0xFE]
    bus.write_i2c_block_data(address, 0x92, getDeviceCommand)

    # Current monitor reads every half a second
    time.sleep(0.5)

    # PECMAC125A address, 0x2A(42)
    # Read data back from 0x55(85), 3 bytes
    # deviceData = [Type of Sensor, Maximum Current, No. of Channels]
    deviceData = bus.read_i2c_block_data(address, 0x55, 3)

    # Convert the data
    typeOfSensor = deviceData[0]
    maxCurrent = deviceData[1]
    numChannels = deviceData[2]

    if numChannels == 0:
        print('No AC Monitor detected. Please check your connection and try again.')
        exit(1)

    uuids = get_uuids(numChannels)
    device_id = uuids[0]

    print('Initializing Device...')
    print('AC monitor with {} channels detected...'.format(numChannels))
    initialization_data = {
        'type': 'initialize',
        'payload': {
            'deviceID': device_id,
            'channels': uuids[1:],
        },
    }
    publish_data(json.dumps(initialization_data))


    # Bytes:
    # 1. PECMAC125A address, 0x2A(42)
    # 2. i2c Header, 0x92(146)
    # Command for reading current
    # 3. 0x6A(106), 4. 0x01(1), 5. 0x01(1), 6. 0x08(8), 7. 0x00(0), 8. 0x00(0) 9. 0x06(6)
    # Header byte-2, command-1, start channel-1, stop channel-8, byte 5 and 6 reserved, checksum
    # Calculate checksum (page 9): https://media.ncd.io/sites/2/20170721134908/Current-Monitoring-Reference-Guide-24.pdf
    #    checksum = Sum of bytes 2-8
    #    checksum = 146+106+1+1+8 = 262 = 00000001 00000110 = 0x06
    #                               256 = 00000001 00000000 = 0x00
    #                        3    4     5     6     7     8     9
    get1ChannelCommand = [0x6A, 0x01, 0x01, 0x02, 0x00, 0x00, 0xFF]
    get2ChannelsCommand = [0x6A, 0x01, 0x01, 0x02, 0x00, 0x00, 0x00]
    get4ChannelsCommand = [0x6A, 0x01, 0x01, 0x02, 0x00, 0x00, 0x02]
    get8ChannelsCommand = [0x6A, 0x01, 0x01, 0x08, 0x00, 0x00, 0x06]    #channels 1-8
    get12ChannelsCommand = [0x6A, 0x01, 0x01, 0x08, 0x00, 0x00, 0x0C]

    getChannelCommand = get1ChannelCommand
    if numChannels == 2:
        getChannelCommand = get2ChannelsCommand
    elif numChannels == 4:
        getChannelCommand = get4ChannelsCommand
    elif numChannels == 8:
        getChannelCommand = get8ChannelsCommand
    elif numChannels == 12:
        getChannelCommand = get12ChannelsCommand

    time.sleep(0.5)

    # Real-time data loop
    prev = [-1] * numChannels
    print('Connected to MQTT. Beginning Energy Usage Collection')
    while (1):
        bus.write_i2c_block_data(address, 0x92, getChannelCommand)

        # PECMAC125A address, 0x2A(42)
        # Read data back from 0x55(85), (No. of Channels * 3 bytes) + 1
        # Single channel = [current MSB1, current MSB, current LSB]
        readings = bus.read_i2c_block_data(address, 0x55, (numChannels * 3) + 1)
        
        # see https://stackoverflow.com/a/25722275
        now = datetime.datetime.now()
        timestamp_micros = (now - epoch) // datetime.timedelta(microseconds=1)
        timestamp_millis = timestamp_micros // 1000

        # Convert the data
        currents = []
        for i in range(0, numChannels):
            bytePos = i * 3
            msb1 = readings[bytePos]
            msb = readings[bytePos + 1]
            lsb = readings[bytePos + 2]
        
            # Convert the data to ampere
            current = (msb1 * 65536 + msb * 256 + lsb) / 1000.0
            currents.append(round(current, 3))
            
        for i in range(0, numChannels):
            if (currents[i] >= 0 and prev[i] != 0):
                channel_id = uuids[i + 1]
                data = {
                    'type': 'usage',
                    'payload': {
                        'deviceID': device_id,
                        'channelID': channel_id,
                        'timestamp': timestamp_millis,
                        'amps': currents[i],
                    }
                }
                #print(data)
                publish_data(json.dumps(data))
            
        prev = currents
        time.sleep(0.5)
