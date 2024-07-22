import argparse

"""This module implements functions that handle the command line interface of the program."""

# Get Arguments from Commandline 
def get_args() -> dict:
  """Creates and configures an argparser for the command line interface and returns the arguments given by the user as a dictionary. 

  Returns:
      dict: The arguments given in the command line.
  """  
  # Get argparser
  argparser = argparse.ArgumentParser(prog="inventurgui", description='A web application to display the content of an .ods (Libre Office Calc) file in a nice way.')
  # Add arguments to argparser
  argparser.add_argument("-c", "--config", dest='config_file', help='specify path to config file, defaults to config.yml')
  argparser.add_argument("-d", "--debug", dest='debug', help='set the log level to debug, defaults to info', action='store_true') 
  argparser.set_defaults(config_file="files/config.yml", log_level='info')
  # Parse args to dictionary
  args:dict = argparser.parse_args()
  return args # Return Args
