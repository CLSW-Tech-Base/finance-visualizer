from visualizer.core import Visualizer
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Finance Visualizer Tool")

    parser.add_argument("--config", help="Path to the JSON config file defining source files and columns", required=True)

    args = parser.parse_args()

    visualizer = Visualizer()

    try:
        visualizer.load_config(args.config)
        visualizer.process_all()
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    main()