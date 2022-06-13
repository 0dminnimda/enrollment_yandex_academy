"""
Main command-line interface for the application
"""

import argparse

from SBDY_app import run

parser = argparse.ArgumentParser(
    prog="SBDY_app", description="Run web app that simulates an online shop")
parser.add_argument("--host", default="localhost",
                    help="change where app will be hosted,"
                    " default is 'localhost'")

args = parser.parse_args()

if __name__ == "__main__":
    run(host=args.host)
