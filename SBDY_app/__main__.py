"""
Main command-line interface for the application
"""

import argparse

from SBDY_app import run

parser = argparse.ArgumentParser(
    prog="SBDY_app", description="Run web app that simulates an online shop")
parser.add_argument("-d", "--docker", action="store_true",
                    help="host app on 0.0.0.0 instead of the localhost")

args = parser.parse_args()

if __name__ == "__main__":
    run(docker=args.docker)
