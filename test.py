import zmq

context = zmq.Context()

s = context.socket(zmq.SUB)
s.connect("tcp://178.79.133.165:9090")
s.setsockopt(zmq.SUBSCRIBE, b'TEST')
while True:
	msg = s.recv().decode()
	print(msg)
