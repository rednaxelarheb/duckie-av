from serial import Serial
from serial.tools.list_ports import comports as get_serial_ports
import struct
from time import sleep, time
from tqdm import tqdm
from new_closed_loop import compute_motor_values


debug_mode = False


# connect to the open serial port
ports = [p[0] for p in get_serial_ports()]
if len(ports) == 0:
    print("Error, couldn't find any open ports")
    exit()
ser = Serial(port=ports[0], baudrate=115200)
ser.flushInput()


last_write = time()

def write_motors(left_motor, right_motor):
	last_write = time()
	left_motor, right_motor = 0, 0
	to_write = struct.pack('hhc', left_motor, right_motor, b'A')
	if debug_mode:
		print("pi->arduino", left_motor, right_motor)
		# print("pi->arduino {:08b}".format(int(to_write.hex(),16))[:-8])
	ser.write(to_write)

start_time = 0
received_first_message = False

bytes_buffer = b""
buffer_i = 0
with tqdm(total=1) as pbar:
	while True:
		if ser.in_waiting > 0:
			new_byte = ser.read()

			if len(bytes_buffer) == 4:
				if not received_first_message:
					start_time = time()
					received_first_message = True

				left_encoder, right_encoder = struct.unpack('<hh', bytes_buffer)
				if debug_mode:
					print("arduino->pi", left_encoder, right_encoder)
					# print("arduino->pi {:08b}".format(int(bytes_buffer.hex(),16)))

				t = time() - start_time
				left_motor, right_motor = compute_motor_values(t, left_encoder, right_encoder)
				write_motors(left_motor, right_motor)


				bytes_buffer = b""
				# pbar.update()  # only to measure communication delay

			else:
				bytes_buffer += new_byte

		else:
			curr_time = time()
			if curr_time - last_write > 0.01:
				write_motors(0, 0)
				sleep(0.01)
