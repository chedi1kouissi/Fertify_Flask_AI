import os
import sys
import logging
import multiprocessing
import time
import subprocess
import platform

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default port configuration
FERTILIZER_PORT = int(os.getenv('FERTILIZER_PORT', 5001))
DISEASE_PORT = int(os.getenv('DISEASE_PORT', 5002))

def kill_process_on_port(port):
    """Kill any process running on the specified port"""
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            if result.stdout:
                # Get the PID from the last column
                for line in result.stdout.strip().split('\n'):
                    if f':{port}' in line and ('LISTENING' in line or 'ESTABLISHED' in line):
                        parts = line.strip().split()
                        if parts:
                            pid = parts[-1]
                            logger.info(f"Found process {pid} using port {port}")
                            try:
                                subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                                logger.info(f"Killed process {pid}")
                                return True
                            except Exception as e:
                                logger.error(f"Failed to kill process {pid}: {e}")
                return False
        else:
            # Unix-based systems
            result = subprocess.run(
                f"lsof -i :{port} | grep LISTEN", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            if result.stdout:
                # Get the PID from the second column
                for line in result.stdout.strip().split('\n'):
                    parts = line.strip().split()
                    if len(parts) > 1:
                        pid = parts[1]
                        logger.info(f"Found process {pid} using port {port}")
                        try:
                            subprocess.run(f'kill -9 {pid}', shell=True)
                            logger.info(f"Killed process {pid}")
                            return True
                        except Exception as e:
                            logger.error(f"Failed to kill process {pid}: {e}")
                return False
        
        logger.info(f"No process found using port {port}")
        return True
    except Exception as e:
        logger.error(f"Error checking for processes on port {port}: {e}")
        return False

def run_fertilizer_service():
    """Start the fertilizer recommendation service"""
    logger.info(f"Starting Fertilizer Recommendation Service on port {FERTILIZER_PORT}")
    # Set environment variables
    os.environ['FERTILIZER_PORT'] = str(FERTILIZER_PORT)
    os.environ['FLASK_ENV'] = 'production'  # Disable debug reloading
    try:
        import fertilizer
        logger.info("Fertilizer service imported successfully")
        fertilizer.start_server(use_reloader=False, debug=False)
    except Exception as e:
        logger.error(f"Failed to start fertilizer service: {e}")
        return

def run_disease_service():
    """Start the disease detection service"""
    logger.info(f"Starting Disease Detection Service on port {DISEASE_PORT}")
    # Set environment variables
    os.environ['DISEASE_PORT'] = str(DISEASE_PORT)
    os.environ['FLASK_ENV'] = 'production'  # Disable debug reloading
    try:
        import disease_predictor
        logger.info("Disease detection service imported successfully")
        disease_predictor.start_server(use_reloader=False, debug=False)
    except Exception as e:
        logger.error(f"Failed to start disease detection service: {e}")
        return

def main():
    """Main controller function to start all services"""
    # Enable Windows multiprocessing support
    multiprocessing.freeze_support()
    
    logger.info("Starting Fertify GreenAI Controller")
    logger.info(f"Fertilizer service will run on port: {FERTILIZER_PORT}")
    logger.info(f"Disease detection service will run on port: {DISEASE_PORT}")
    
    # Clean up existing processes
    logger.info("Checking for existing processes...")
    kill_process_on_port(FERTILIZER_PORT)
    kill_process_on_port(DISEASE_PORT)
    
    # Set multiprocessing start method
    if sys.platform == 'win32':
        # Windows requires 'spawn' for Flask apps in multiprocessing
        multiprocessing.set_start_method('spawn', force=True)
    elif hasattr(multiprocessing, 'get_context'):
        # On Unix systems, 'fork' is usually faster
        multiprocessing.set_start_method('fork', force=True)
    
    # Create processes for each service
    fertilizer_process = multiprocessing.Process(target=run_fertilizer_service)
    disease_process = multiprocessing.Process(target=run_disease_service)
    
    try:
        # Start all processes
        fertilizer_process.start()
        logger.info("Fertilizer service process started")
        
        # Wait a moment before starting the next service
        time.sleep(1)
        
        disease_process.start()
        logger.info("Disease detection service process started")
        
        # Print access information
        logger.info("\n" + "="*50)
        logger.info("Fertify GreenAI Services Running")
        logger.info("="*50)
        logger.info(f"Fertilizer API: http://localhost:{FERTILIZER_PORT}/predict_fertilizer/")
        logger.info(f"Disease Detection API: http://localhost:{DISEASE_PORT}/predict_disease/")
        logger.info("="*50 + "\n")
        
        # Keep the script running
        while fertilizer_process.is_alive() and disease_process.is_alive():
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down services...")
    except Exception as e:
        logger.error(f"Error in controller: {e}")
    finally:
        # Clean up processes if still running
        if fertilizer_process.is_alive():
            logger.info("Terminating fertilizer service...")
            fertilizer_process.terminate()
            fertilizer_process.join(timeout=5)
            if fertilizer_process.is_alive():
                logger.warning("Fertilizer service did not terminate gracefully, forcing...")
                if hasattr(fertilizer_process, 'kill'):
                    fertilizer_process.kill()
            logger.info("Fertilizer service terminated")
        
        if disease_process.is_alive():
            logger.info("Terminating disease detection service...")
            disease_process.terminate()
            disease_process.join(timeout=5) 
            if disease_process.is_alive():
                logger.warning("Disease service did not terminate gracefully, forcing...")
                if hasattr(disease_process, 'kill'):
                    disease_process.kill()
            logger.info("Disease detection service terminated")
        
        logger.info("All services shut down. Exiting.")

if __name__ == "__main__":
    main() 