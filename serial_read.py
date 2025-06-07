import asyncio
import serial
import struct
from dataclasses import dataclass

@dataclass
class Payload:
    stance: bool
    p: tuple[float, float, float]
    v: tuple[float, float, float]
    w_m: tuple[float, float, float]
    a_m: tuple[float, float, float]
    a_b: tuple[float, float, float]
    a_w: tuple[float, float, float]
    q: tuple[float, float, float, float]
    ag: tuple[float, float, float]  # Added new vector field ag
    fa: tuple[float,float,float]


HEADER = b'\xA5\x5A'
HEADER_SIZE = 2
DATA_SHAPE = "<?3f3f3f3f3f3f4f3f3f"
PACKET_SIZE = HEADER_SIZE + struct.calcsize(DATA_SHAPE)


class AsyncSerialReader:
    def __init__(self, port, baudrate=230400):
        self.ser = serial.Serial(port, baudrate, timeout=0)
        self.buffer = bytearray()
        self.loop = asyncio.get_event_loop()

    def _read_bytes(self):
        return self.ser.read(self.ser.in_waiting or 1)

    async def read_packet(self):
        # start_time = time.perf_counter()
        while True:
            # Offload blocking read to thread pool
            data = await self.loop.run_in_executor(None, self._read_bytes)
            self.buffer += data

            idx = self.buffer.find(HEADER)
            if idx < 0 or len(self.buffer) < idx + PACKET_SIZE:
                continue

            packet = self.buffer[idx : idx + PACKET_SIZE]
            self.buffer = self.buffer[idx + PACKET_SIZE :]
            payload_data = packet[HEADER_SIZE:]
            # _req = time.perf_counter() - start_time later

            unpacked_data = struct.unpack(DATA_SHAPE, payload_data)
            payload = Payload(
                stance=unpacked_data[0],
                p=unpacked_data[1:4],
                v=unpacked_data[4:7],
                w_m=unpacked_data[7:10],  # Added w_m
                a_m=unpacked_data[10:13],
                a_b=unpacked_data[13:16],
                a_w=unpacked_data[16:19],
                q=unpacked_data[19:23],
                ag=unpacked_data[23:26],  # Added new field 'ag'
                fa=unpacked_data[26:29]
            )

            return payload

    def close(self):
        if self.ser.is_open:
            self.ser.close()
