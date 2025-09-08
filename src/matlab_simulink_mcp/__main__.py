import argparse
from matlab_simulink_mcp.server import run

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--console", action="store_true", help="Keep console open")
    args = parser.parse_args()

    run(console=args.console)

if __name__ == "__main__":
    main()
