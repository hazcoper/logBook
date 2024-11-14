import importlib
import inspect
import logging
import threading
import signal
import sys
from config_parser import ConfigParser

class Launcher:
    
    def __init__(self):
        """
        Initializes the Launcher with a list of modules to be launched.
        """
        # Load the configuration class
        self.config = ConfigParser()
        self.config.loadConfig()
        
        # Retrieve the list of modules from the configuration (assuming it is a comma-separated string)
        self.modules_list = self.config.get("modules")

        # Set up logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.set_logging_level(logging.INFO)  # Default logging level

        # List to keep track of active threads
        self.threads = []
    
    def set_logging_level(self, level):
        """
        Sets the logging level. Level can be logging.DEBUG, logging.INFO, etc.
        """
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger.setLevel(level)
        self.logger.info(f"Logging level set to {logging.getLevelName(level)}")
    
    def launch_single_module(self, module_name):
        """
        Given a module name, this method will dynamically import and launch it.
        module_name is the name of the file that contains the class/function to be launched.
        """
        try:
            # Dynamically import the module
            module = importlib.import_module(module_name)
            self.logger.info(f"Launching: {module_name}")

            # Get the list of classes defined in the module
            classes = inspect.getmembers(module, inspect.isclass)
            module_classes = [cls for cls_name, cls in classes if cls.__module__ == module_name]
            self.logger.debug(f"Classes found in module {module_name}: {module_classes}")

            # Check for ambiguity or absence of classes
            if len(module_classes) > 1:
                self.logger.error(f"Module {module_name} has more than one class defined. Cannot determine which one to launch.")
                raise ValueError(f"Module {module_name} has more than one class defined. Cannot determine which one to launch.")
            if len(module_classes) == 0:
                self.logger.error(f"Module {module_name} does not have any class defined.")
                raise ValueError(f"Module {module_name} does not have any class defined.")
        
            # Instantiate the first class found
            module_instance = module_classes[0]()

            # If the module has a main function or a specific function to run, you can call it here
            if hasattr(module_instance, 'main'):
                self.logger.info(f"Calling 'main' function of class in {module_name}")
                module_instance.main()
            else:
                self.logger.warning(f"Module {module_name} does not have a 'main' function.")
        
        except ImportError as e:
            self.logger.error(f"Could not import module {module_name}. Exception: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"An error occurred while launching module {module_name}. Exception: {e}")
            raise

    def orchestrate_modules(self):
        """
        Orchestrates the launching of all modules in the modules_list by creating a thread for each module.
        Handles graceful shutdown when Ctrl+C (SIGINT) is received.
        """
        def launch_thread(module_name):
            try:
                self.launch_single_module(module_name)
            except Exception as e:
                self.logger.error(f"Failed to launch module {module_name}. Error: {e}")

        def signal_handler(sig, frame):
            self.logger.info("Ctrl+C received. Stopping all threads...")
            for thread in self.threads:
                if thread.is_alive():
                    self.logger.info(f"Waiting for thread {thread.name} to finish...")
                    thread.join(timeout=1)
            self.logger.info("All threads stopped. Exiting.")
            sys.exit(0)

        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)

        # Create and start a thread for each module
        for module in self.modules_list:
            self.logger.info(f"Creating thread for module {module}")
            thread = threading.Thread(target=launch_thread, args=(module,))
            thread.start()
            self.threads.append(thread)
            self.logger.debug(f"Started thread for module {module}")

        # Keep the main thread alive to handle signal interruptions
        for thread in self.threads:
            thread.join()

if __name__ == "__main__":
    my_launcher = Launcher()
    my_launcher.set_logging_level(logging.DEBUG)
    my_launcher.orchestrate_modules()
