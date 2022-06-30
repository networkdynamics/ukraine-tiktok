import argparse
import json

import matplotlib.pyplot as plt

def main(args):
    with open(args.input, 'r') as f:
        tiktoks = json.load(f)

    plt.show()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input')
    args = parser.parse_args()

    main(args)