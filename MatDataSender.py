import scipy.io
import time
import socket
import json
import threading
import sys
import numpy as np

class MatDataSender:
    def __init__(self, mat_file_path, variable_name=None, port=12345):
        """
        Initialize the data sender with the MAT file path and optional port number.
        
        Args:
            mat_file_path (str): Path to the .mat file
            variable_name (str): Name of the variable to use ('y_pred' or 'y_true')
            port (int): Port number for UDP communication
        """
        self.port = port
        self.running = False
        
        # Load MAT file
        try:
            mat_contents = scipy.io.loadmat(mat_file_path)
            
            if 'y_pred' not in mat_contents or 'y_true' not in mat_contents:
                raise ValueError("Could not find y_pred or y_true in the MAT file")
            
            print("\nAvailable variables:")
            print(f"y_pred: shape={mat_contents['y_pred'].shape}, type={mat_contents['y_pred'].dtype}")
            print(f"y_true: shape={mat_contents['y_true'].shape}, type={mat_contents['y_true'].dtype}")
            
            if variable_name is None:
                variable_name = 'y_pred'  # default to y_pred if none specified
                
            if variable_name not in ['y_pred', 'y_true']:
                raise ValueError("variable_name must be either 'y_pred' or 'y_true'")
                
            self.data = mat_contents[variable_name]
            
            self.data = self.data.flatten().astype(float)
            
            print(f"\nUsing variable: {variable_name}")
            print(f"Number of values: {len(self.data)}")
            print(f"Data range: min={np.min(self.data):.3f}, max={np.max(self.data):.3f}")
            
        except Exception as e:
            print(f"Error loading MAT file: {e}")
            sys.exit(1)
            
        # Setup UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def start(self):
        """Start sending data to Unity"""
        self.running = True
        self.sender_thread = threading.Thread(target=self._send_data)
        self.sender_thread.start()
        
    def stop(self):
        """Stop sending data"""
        self.running = False
        if hasattr(self, 'sender_thread'):
            self.sender_thread.join()
        
    def _send_data(self):
        """Send data to Unity at 20ms intervals"""
        index = 0
        start_time = time.time()
        
        while self.running and index < len(self.data):
            current_value = float(self.data[index])  # Convert to float for JSON serialization
            
            # Package data with index for synchronization
            message = json.dumps({
                "index": index,
                "value": current_value
            })
            
            # Send to Unity
            self.sock.sendto(message.encode(), ('127.0.0.1', self.port))
            
            index += 1
            
            # Calculate next send time (20ms intervals)
            next_time = start_time + (index * 0.02)  # 20ms = 0.02s
            sleep_time = next_time - time.time()
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            
        print("Finished sending all data")

def main():
    if len(sys.argv) < 2:
        print("Usage: python mat_data_sender.py <path_to_mat_file> [variable_name]")
        print("variable_name can be 'y_pred' or 'y_true'")
        sys.exit(1)
    
    mat_file_path = sys.argv[1]
    variable_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    sender = MatDataSender(mat_file_path, variable_name)
    
    try:
        sender.start()
        print("\nPress Ctrl+C to stop sending data")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sender.stop()
        print("\nStopped data sending")

if __name__ == "__main__":
    main()