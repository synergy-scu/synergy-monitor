import os
from uuid import uuid4 as uuidv4

def device_uuid():
	exists = os.path.isfile('uuid.txt')

	if exists:
		f = open('uuid.txt', 'r')
		uuid = f.read()

		return uuid

	else:
		f = open('uuid.txt', 'w')

		uuid = str(uuidv4())
		f.write(uuid)

		f.close()
		return uuid
		
