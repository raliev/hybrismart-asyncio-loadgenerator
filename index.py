#!/usr/bin/python3

from http_load import HTTPLoadGenerator
import argparse


# use arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument("--inputfile", "-i", help="text file with the list of urls", default="urls.txt")
parser.add_argument("--lfrom", "-lf", help="start # of url from the file", default=0, type=int)
parser.add_argument("--lto" , "-lt", help="end # of url from the file", default=9, type=int)
parser.add_argument("--wait", "-w", help="waittime between batches", default=3, type=int)
parser.add_argument("--size", "-s", help="size of the batch", default=10, type=int)

# parse arguments
args = parser.parse_args()

# configure the test
generator = HTTPLoadGenerator(seed_file=args.inputfile,
  spare_time=args.wait,
  rps=args.size,
  from_line=args.lfrom,
  to_line=args.lto
)

# execute the process
generator.start()
# save output to file
generator.save_results_to_file()

