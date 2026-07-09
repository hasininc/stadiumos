
import sys
import logging
import signal

from pathlib import Path
# Set PYTHONPATH to contain app folder
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.stream.stream_processor import StreamProcessor

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cv-edge")

processor = None

def signal_handler(sig, frame):
    logger.info("Signal received. Shutting down Edge CV service...")
    if processor:
        processor.stop()
    sys.exit(0)

def main():
    global processor
    logger.info("=========================================")
    logger.info("STADIUMOS EDGE COMPUTER VISION STARTING")
    logger.info("=========================================")
    
    # Catch SIGINT (Ctrl+C) and SIGTERM signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        processor = StreamProcessor()
        processor.start()
    except Exception as e:
        logger.critical(f"Fatal error in Edge CV runtime: {e}", exc_info=True)
        if processor:
            processor.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
