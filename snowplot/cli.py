"""Console script for snowplot."""
import argparse
import sys
from .snowplot import make_vertical_plot

def main():
    """Console script for snowplot."""
    parser = argparse.ArgumentParser(description='Generate vertical profiles'
                                                 ' of snow data.')
    parser.add_argument('config_file', help='path to config_file')
    args = parser.parse_args()

    # Provide a opportunity to look at lots
    if args.config_file == None:
        print("Please provide a config file for plots")
        sys.exit()

    make_vertical_plot(args.config_file)

    return 0


if __name__ == "__main__":
    main()
