import argparse
import logging
from argparse import Namespace

"""This module implements functions that handle the command line interface of the program."""

# Get Arguments from Commandline 
def get_args() -> Namespace:
  """Creates and configures an argparser for the command line interface and returns the arguments given by the user as a dictionary. 

  Returns:
      dict: The arguments given in the command line.
  """  
  # Get argparser
  argparser = argparse.ArgumentParser(prog="inventurgui", description='A web application to display the content of an .ods (Libre Office Calc) file in a nice way.')
  # Add arguments to argparser
  argparser.add_argument("-c", "--helper", dest='config_file', help='specify path to helper file, defaults to files/helper.yml')
  argparser.add_argument("-d", "--dev", dest='debug', help='set the log level to debug, enable reloader', action='store_true')
 # argparser.add_argument("-p", "--set-password", dest='set_pass', help='set the password required for the admin panel (configuration)', action='store_true')
 # argparser.add_argument("-u", "--users", dest='users_file', help='specify path to users_file, defaults to files/users.yml')
  argparser.set_defaults(config_file="config.yml", log_level='info', users_file='../../files/users.yml')
  # Parse args to dictionary
  args:Namespace = argparser.parse_args()
  if args.debug:
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.INFO)
  logging.debug(f"Args: {args}")
  return args # Return Args

ARGS = get_args()