import argparse
import sys

# Get Arguments from Commandline 
def get_args() -> dict:
    # Get Argparser and add arguments
    argparser = argparse.ArgumentParser(prog="inventurgui", description='A web application to display the content of an .ods (Libre Office Calc) file in a nice way.')
    argparser.add_argument("-c", "--config", dest='config_file', help='specify path to config file, defaults to config.yml')
    argparser.add_argument("-d", "--debug", dest='debug', help='set the log level to debug, defaults to info', action='store_true') 
    argparser.add_argument("-p", "--print", dest='print', help='print data to stdout for debugging', action='store_true')
    argparser.set_defaults(config_file="config.yml", log_level='info')
   
    # Show help if no argument specified
  #  if len(sys.argv) <= 1:
   #     sys.argv.append('--help')
    args:dict = argparser.parse_args()
    return args
