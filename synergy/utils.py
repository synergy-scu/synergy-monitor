import os
from uuid import uuid4 as uuidv4

def get_uuids(numChannels):
    exists = os.path.isfile('uuid.txt')

    if exists:
        f = open('uuid.txt', 'r')
        uuids = f.readlines()
        return uuids

    uuids = []
    f = open('uuid.txt', 'w')

    device_uuid = str(uuidv4())
    f.write(device_uuid + "\n")
    uuids.append(device_uuid)

    for _ in range(0, numChannels):
        ch_uuid = str(uuidv4())
        f.write(ch_uuid + "\n")
        uuids.append(ch_uuid)

    f.close()
    return uuids
