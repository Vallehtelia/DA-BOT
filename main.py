#!/usr/bin/env python3
"""
Main entry point for the AI Agent Platform.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from tools.overseer import Overseer
from tools.models import ModelManager

def setup_logging(verbosity: str = "INFO"):
    """Setup logging configuration."""
    log_level = getattr(logging, verbosity.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('artifacts/logs/main.log')
        ]
    )

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Agent Platform",
        epilog="""
Examples:
  # Test mode
  python3 main.py --goal "test goal" --test
  
  # Run with retries and debug
  python3 main.py --goal "check monitor resolution" --retries 5 --debug
  
  # Disable killswitch for testing
  python3 main.py --goal "test" --no-killswitch --debug
        """
    )
    parser.add_argument("--goal", "-g", required=True, help="Goal to accomplish")
    parser.add_argument("--verbosity", "-v", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging verbosity")
    parser.add_argument("--test", "-t", action="store_true", help="Run in test mode")
    parser.add_argument("--retries", "-r", type=int, default=3, help="Maximum number of retry attempts (default: 3)")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode (prints detailed responses)")
    parser.add_argument("--no-killswitch", action="store_true", help="Disable killswitch for testing")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbosity)
    logger = logging.getLogger("main")
    
    logger.info("Starting AI Agent Platform")
    
    try:
        # Initialize model manager first to ensure models are loaded
        logger.info("Initializing ModelManager...")
        model_manager = ModelManager()
        
        # Initialize overseer
        overseer = Overseer()
        
        # Enable debug mode if requested
        if args.debug:
            logger.info("Debug mode enabled - will print detailed responses")
            # Update mode.json to enable debug mode
            mode_file = Path("config/mode.json")
            if mode_file.exists():
                try:
                    import json
                    with open(mode_file, 'r') as f:
                        mode_config = json.load(f)
                    mode_config["debug_mode"] = True
                    mode_config["verbosity"] = "high"
                    with open(mode_file, 'w') as f:
                        json.dump(mode_config, f, indent=2)
                    logger.info("Updated mode.json to enable debug mode")
                except Exception as e:
                    logger.warning(f"Failed to update mode.json: {e}")
        
        # Disable killswitch if requested
        if args.no_killswitch:
            logger.info("Killswitch disabled for testing")
            killswitch_file = Path("control/killswitch.on")
            if killswitch_file.exists():
                killswitch_file.unlink()
                logger.info("Removed killswitch file")
        
        if args.test:
            logger.info("Running in test mode")
            # For now, just show status
            status = overseer.get_status()
            logger.info(f"System status: {status}")
        else:
            # Run the actual goal with retry logic
            logger.info(f"Executing goal: {args.goal}")
            max_retries = args.retries
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    success = overseer.run(args.goal)
                    
                    if success:
                        logger.info("Goal completed successfully!")
                        break
                    else:
                        retry_count += 1
                        if retry_count < max_retries:
                            logger.warning(f"Goal failed! Attempt {retry_count}/{max_retries}. Retrying...")
                            # Wait a bit before retrying
                            import time
                            time.sleep(2)
                        else:
                            logger.error(f"Goal failed after {max_retries} attempts. Giving up.")
                            sys.exit(1)
                            
                except Exception as e:
                    retry_count += 1
                    logger.error(f"Error during execution (attempt {retry_count}/{max_retries}): {e}")
                    if retry_count >= max_retries:
                        logger.error(f"Max retries reached. Exiting.")
                        sys.exit(1)
                    else:
                        logger.warning("Retrying...")
                        import time
                        time.sleep(2)
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        sys.exit(1)
    finally:
        # Shutdown overseer
        try:
            overseer.shutdown()
        except:
            pass
        
        logger.info("Platform shutdown complete")

if __name__ == "__main__":
    main()
