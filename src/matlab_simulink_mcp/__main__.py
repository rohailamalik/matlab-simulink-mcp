import argparse
import matlab_simulink_mcp.server as server

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--console", action="store_true", help="Keep console open.")
    args = parser.parse_args()

    server.console = args.console
    server.run()

if __name__ == "__main__":
    main()
