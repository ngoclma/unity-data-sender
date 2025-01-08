import pandas as pd
import time
import socket
import json
import threading
import sys
import numpy as np

class ExcelDataSender:
    def __init__(self, excel_file_path, sheet_name=None, port=12345):
        """
        Initialize the data sender with the Excel file path and optional port number.
        
        Args:
            excel_file_path (str): Path to the Excel file
            sheet_name (str): Name of the sheet to use. If None, will show available sheets
            port (int): Port number for UDP communication
        """
        self.port = port
        self.running = False
        
        try:
            # Read list of sheets first
            excel_file = pd.ExcelFile(excel_file_path)
            available_sheets = excel_file.sheet_names
            
            print("\nAvailable sheets in Excel file:")
            for sheet in available_sheets:
                # Read the sheet to get the width (number of columns)
                sheet_data = pd.read_excel(excel_file_path, sheet_name=sheet, header=None)
                print(f"{sheet}: {sheet_data.shape[1]} values")
            
            # Select which sheet to use
            if sheet_name is None:
                if len(available_sheets) > 0:
                    sheet_name = available_sheets[0]
                else:
                    raise ValueError("No sheets found in Excel file")
            
            if sheet_name not in available_sheets:
                raise ValueError(f"Sheet '{sheet_name}' not found in Excel file")
            
            # Read the selected sheet
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=None)
            
            # Convert the first row to numpy array
            self.data = df.iloc[0, :].to_numpy().astype(float)
            
            print(f"\nUsing sheet: {sheet_name}")
            print(f"Number of values: {len(self.data)}")
            print(f"Data range: min={np.min(self.data):.3f}, max={np.max(self.data):.3f}")
            print(f"First few values: {self.data[:5]}")
            
        except Exception as e:
            print(f"Error loading Excel file: {e}")
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
            
            if index % 50 == 0:  # Print progress every 50 values
                print(f"Sent value {index}/{len(self.data)}: {current_value:.3f}")
            
            index += 1
            
            # Calculate next send time (20ms intervals)
            next_time = start_time + (index * 0.02)  # 20ms = 0.02s
            sleep_time = next_time - time.time()
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            
        print("Finished sending all data")

def main():
    if len(sys.argv) < 2:
        print("Usage: python excel_data_sender.py <path_to_excel_file> [sheet_name]")
        print("sheet_name is optional. If not provided, first sheet will be used")
        sys.exit(1)
    
    excel_file_path = sys.argv[1]
    sheet_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    sender = ExcelDataSender(excel_file_path, sheet_name)
    
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