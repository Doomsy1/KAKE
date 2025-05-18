# Artificial Intelligence was used in this file to : debug errors, and research TCP (previously serial communication)


import socket
import errno
import time
import select
import threading
import queue

from camera import Camera
from hello import BallDetector

def bytes_to_string(data):
    try:
        return data.decode('utf-8')
    except:
        try:
            return data.decode('ascii')
        except:
            return f"<hex: {data.hex()}>"

class TCPClient:
    def __init__(self, ball_detector: BallDetector, host='10.249.222.198', port=55000):
        self.ball_detector = ball_detector
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.send_queue = queue.Queue()
        self.lock = threading.Lock()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            print(f"Connecting to {self.host}:{self.port}")
            self.socket.connect((self.host, self.port))
            print("Connected to server.")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.socket = None # get rid of socket if borken
            return False

    def send_messages(self):
        while self.running or not self.send_queue.empty():
            try:
                message = self.send_queue.get(timeout=0.1)
                if message == "QUIT":
                    if self.running:
                        print("Sender thread received QUIT signal.")
                    break
                
                if self.socket:
                    with self.lock:
                        print(f"Attempting to send via socket: '{message}'")
                        self.socket.sendall((message + '\n').encode('utf-8'))
                        print(f"Successfully sent via socket: '{message}'")
                else:
                    print("Send error: Socket is not connected.")
            except queue.Empty:
                if not self.running and self.send_queue.empty():
                    break
                continue
            except Exception as e:
                print(f"Unexpected send error: {e}")
                self.running = False # stop
                break
        print("Sender thread stopped.")

    def data_producer_loop(self):
        print("Data producer thread started.")
        try:
            while self.running:
                start_time = time.time()
                result = self.ball_detector.getTarget()
                end_time = time.time()
                
                delta_time = end_time - start_time
                fps = 1 / delta_time if delta_time > 0 else 0

                if result is not None:
                    x, y, z = result
                    message_to_send = f"{x:.2f},{y:.2f},{z:.2f}" # Format: float,float,float
                    self.send_queue.put(message_to_send)
                    print(f'FPS: {fps:.2f} | BallDetector: Target found ({x:.2f}, {y:.2f}, {z:.2f}). Queued for sending: "{message_to_send}"')
                else:
                    print(f'FPS: {fps:.2f} | BallDetector: No target found. Nothing to send.')

                if not self.running:
                    break

        except Exception as e:
            print(f"Error in data producer loop: {e}")
        finally:
            print("Data producer loop stopped.")
            self.running = False # bruh stop

    def start(self):
        if not self.connect():
            print("Failed to connect to server. Client will not start.")
            return

        self.running = True

        self.producer_thread = threading.Thread(target=self.data_producer_loop, name="DataProducerThread")
        self.send_thread = threading.Thread(target=self.send_messages, name="SendMessageThread")
        
        self.producer_thread.daemon = True 
        self.send_thread.daemon = True
        
        self.producer_thread.start()
        self.send_thread.start()

        try:
            while self.running:
                if not self.producer_thread.is_alive() and self.running:
                    print("Data producer thread has unexpectedly stopped. Shutting down client.")
                    self.running = False
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down client...")
        finally:
            self.running = False
            
            print("Sending QUIT signal to message queue...")
            self.send_queue.put("QUIT")

            threads_to_join = []
            if hasattr(self, 'producer_thread') and self.producer_thread.is_alive():
                threads_to_join.append(self.producer_thread)
            if hasattr(self, 'send_thread') and self.send_thread.is_alive():
                threads_to_join.append(self.send_thread)

            for t in threads_to_join:
                print(f"Waiting for {t.name} to finish...")
                t.join(timeout=2.0) # waiting for duh threads
                if t.is_alive():
                    print(f"{t.name} did not finish in time.")
            
            if self.socket:
                print("Closing socket...")
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                except socket.error as e:
                    if e.errno != errno.ENOTCONN:
                         print(f"Error during socket shutdown: {e}")
                finally:
                    self.socket.close()
                    self.socket = None
            print("TCP Client shut down.")

def main():
    print("Initializing cameras and ball detector...")
    try:
        left_camera = Camera(0)
        right_camera = Camera(1)
        ball_detector = BallDetector(left_camera, right_camera)
        print("Initialization complete.")
    except Exception as e:
        print(f"Error initializing cameras or BallDetector: {e}")
        print("Please ensure cameras are connected and configured correctly, and all dependencies are installed.")
        return

    # create and start the TCP client
    client = TCPClient(ball_detector, host='10.249.222.198', port=55000)
    client.start()

if __name__ == "__main__":
    main()
