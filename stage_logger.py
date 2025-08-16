#!/usr/bin/env python3
"""
TEM Stage Position Logger using PyJEM API

This script continuously logs TEM stage position data to a CSV file
until manually stopped (Ctrl+C).

Requirements:
- PyJEM library installed
- Active connection to TEM microscope

Usage:
    python tem_stage_logger.py [output_file] [interval]
    
Arguments:
    output_file: CSV file to save data (default: C:\jeol_dnr\SynergyED_stage_pos_log.csv)
    interval: Logging interval in seconds (default: 0.1)
"""

import sys
import time
import csv
import signal
from datetime import datetime
from pathlib import Path

from PyJEM import TEM3


class StagePositionLogger:
    def __init__(self, output_file=r"C:\jeol_dnr\SynergyED_stage_pos_log.csv", interval=0.1):
        self.output_file = Path(output_file)
        self.interval = interval
        self.running = True
        self.tem = None
        self.csv_writer = None
        self.csv_file = None
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.running = False
        
    def initialize_tem(self):
        """Initialize the TEM connection"""
        try:
            # Try to connect to the TEM
            self.tem = TEM3
            print("Successfully connected to TEM.")
            return True
        except Exception as e:
            print(f"Failed to connect to TEM: {e}")
            return False
    
    def get_stage_position(self):
        """Get current stage position from TEM"""
        try:
            # Get stage position data
            stage_data = self.tem.Stage3().GetPos()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'x_position': stage_data[0],
                'y_position': stage_data[1],
                'z_position': stage_data[2],
                'alpha_tilt': stage_data[3],
                'beta_tilt': stage_data[4]
            }
        except Exception as e:
            print(f"Error reading stage position: {e}")
            return None
    
    def setup_csv_file(self):
        """Set up CSV file and writer"""
        try:
            # Create output directory if it doesn't exist
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Open file in append mode
            file_exists = self.output_file.exists()
            self.csv_file = open(self.output_file, 'a', newline='')
            
            fieldnames = ['timestamp', 'x_position', 'y_position', 'z_position', 
                         'alpha_tilt', 'beta_tilt']
            
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                self.csv_writer.writeheader()
                print(f"Created new log file: {self.output_file}")
            else:
                print(f"Appending to existing log file: {self.output_file}")
                
            return True
        except Exception as e:
            print(f"Error setting up CSV file: {e}")
            return False
    
    def log_position(self, position_data):
        """Log position data to CSV file"""
        try:
            self.csv_writer.writerow(position_data)
            self.csv_file.flush()  # Ensure data is written immediately
            return True
        except Exception as e:
            print(f"Error writing to CSV: {e}")
            return False
    
    def run(self):
        """Main logging loop"""
        print("TEM Stage Position Logger Starting...")
        print(f"Output file: {self.output_file}")
        print(f"Logging interval: {self.interval} seconds")
        print("Press Ctrl+C to stop logging\n")
        
        # Initialize components
        if not self.initialize_tem():
            print("Failed to initialize TEM. Exiting.")
            return False
            
        if not self.setup_csv_file():
            print("Failed to setup CSV file. Exiting.")
            return False
        
        # Main logging loop
        log_count = 0
        start_time = time.time()
        
        try:
            while self.running:
                # Get stage position
                position_data = self.get_stage_position()
                
                if position_data:
                    # Log to file
                    if self.log_position(position_data):
                        log_count += 1
                        
                        # Print status every 10 logs
                        if log_count % 10 == 0:
                            elapsed = time.time() - start_time
                            rate = log_count / elapsed if elapsed > 0 else 0
                            print(f"Logged {log_count} entries "
                                  f"(Rate: {rate:.1f} entries/sec)")
                    
                # Wait for next interval
                time.sleep(self.interval)
                
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
        finally:
            self.cleanup()
            
        return True
    
    def cleanup(self):
        """Clean up resources"""
        print(f"\nCleaning up...")
        
        if self.csv_file:
            self.csv_file.close()
            print(f"Closed log file: {self.output_file}")
            
        if self.tem:
            try:
                # Close TEM connection if applicable
                if hasattr(self.tem, 'disconnect'): #Needs checking !! (seems to work, check when in the TEM room too!)
                    self.tem.connect()
                elif hasattr(self.tem, 'close'):
                    self.tem.close()
            except Exception as e:
                print(f"Error closing TEM connection: {e}")
        
        print("Cleanup complete.")


def get_user_parameters():
    """Interactive parameter setup with user confirmation"""
    print("=== TEM Stage Position Logger Configuration ===\n")
    
    # Default values
    default_output = r"C:\jeol_dnr\SynergyED_stage_pos_log.csv"
    default_interval = 0.1
    
    # Check command line arguments first
    output_file = default_output
    interval = default_interval
    
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            interval = float(sys.argv[2])
        except ValueError:
            print(f"Invalid interval: {sys.argv[2]}. Using default: {interval}")
    
    while True:
        # Display current settings
        print(f"Current Configuration:")
        print(f"  Output file: {output_file}")
        print(f"  Output directory: {Path(output_file).parent}")
        print(f"  Logging interval: {interval} seconds ({1/interval:.1f} Hz)")
        print(f"  File will be {'appended to' if Path(output_file).exists() else 'created'}")
        
        # Check if directory is writable
        try:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            test_file = Path(output_file).parent / "test_write.tmp"
            test_file.touch()
            test_file.unlink()
            print(f"  ✓ Directory is writable")
        except Exception as e:
            print(f"  ✗ Directory access error: {e}")
        
        print("\nOptions:")
        print("  1. Start logging with these settings")
        print("  2. Change output file path")
        print("  3. Change logging interval")
        print("  4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            break
        elif choice == "2":
            new_output = input(f"Enter new output file path (current: {output_file}): ").strip()
            if new_output:
                output_file = new_output
        elif choice == "3":
            try:
                new_interval = float(input(f"Enter new interval in seconds (current: {interval}): ").strip())
                if new_interval > 0:
                    interval = new_interval
                else:
                    print("Interval must be positive!")
            except ValueError:
                print("Invalid interval! Please enter a number.")
        elif choice == "4":
            print("Exiting...")
            return None, None
        else:
            print("Invalid choice! Please enter 1, 2, 3, or 4.")
        
        print("\n" + "="*50 + "\n")
    
    return output_file, interval


def confirm_operation():
    """Final confirmation before starting logging"""
    print("\n" + "="*50)
    print("IMPORTANT INSTRUCTIONS:")
    print("="*50)
    print("• The logger will run continuously until stopped")
    print("• To STOP logging safely, press Ctrl+C (NOT the X button)")
    print("• Pressing Ctrl+C will:")
    print("  - Stop data collection gracefully")
    print("  - Close the CSV file properly")
    print("  - Disconnect from the TEM safely")
    print("• Do NOT close the terminal window or kill the process")
    print("• The CSV file will be updated in real-time")
    print("="*50)
    
    while True:
        response = input("\nDo you understand these instructions and want to start logging? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def main():
    """Main function"""
    print("TEM Stage Position Logger")
    print("========================\n")
    
    # Get user parameters
    output_file, interval = get_user_parameters()
    
    if output_file is None:  # User chose to exit
        sys.exit(0)
    
    # Final confirmation
    if not confirm_operation():
        print("Logging aborted by user.")
        sys.exit(0)
    
    print("\nStarting TEM Stage Position Logger...")
    
    # Create and run logger
    logger = StagePositionLogger(output_file, interval)
    success = logger.run()
    
    if success:
        print("Logging completed successfully.")
    else:
        print("Logging failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()