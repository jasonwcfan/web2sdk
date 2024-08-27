import argparse
import threading
import itertools
import time
import sys
from typing import Any, Optional, Sequence, Union
from api2swagger.main import main as api2swagger_main
from swagger2sdk.main import construct_sdk

def show_loading_indicator(stop_event):
    for char in itertools.cycle(['|', '/', '-', '\\']):
        if stop_event.is_set():
            break
        sys.stdout.write(f'\Working... {char}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!          \n')

def main():
  parser = argparse.ArgumentParser(
    description="Converts a mitmproxy dump file or HAR to a swagger schema."
  )
  parser.add_argument(
    "-i",
    "--interactive",
    help="Run in interactive mode",
    action="store_true",
    required=False,
  )

  parser.add_argument(
    "-r",
    "--requests-path",
    help="Path to a mitmproxy dump file or HAR",
    required=False,
  )

  parser.add_argument(
    "-b",
    "--base-url",
    help="Base url for the API to reverse engineer",
    required=False,
  )

  parser.add_argument(
    "-s",
    "--sdk-name",
    help="Name for the SDK class. Will also be used as the filename for the OpenAPI schema.",
    required=False,
  )

  args = parser.parse_args()

  sdk_location = "swagger2sdk/generated"

  if not args.interactive:
    if not args.requests_path or not args.sdk_name or not args.base_url:
      parser.error("--requests-path, --sdk-name, and --base-url are required when not running in --interactive mode.")
    
    openapi_path = f"api2swagger/generated/{args.sdk_name}.yaml"
   
    api2swagger_main(args.sdk_name, ["--input", args.requests_path, "--output", openapi_path, "--api-prefix", args.base_url, "--format", "flow"])
    print("OpenAPI schema generated successfully at: ", openapi_path)
    construct_sdk(openapi_path, args.sdk_name, sdk_location)
    print("SDK generated successfully at: ", f"{sdk_location}/{args.sdk_name}.py")
  else:
    while True:
      requests_path = input("Enter the path to the mitmproxy dump file or HAR: ")
      base_url = input("Enter the base URL for the API (e.g. https://api.finic.ai/v1): ")
      sdk_name = input("Enter a name for the generated SDK (e.g. FinicAPI): ")
      openapi_path = f"api2swagger/generated/{sdk_name}.yaml"

      # stop_event = threading.Event()
      # loading_thread = threading.Thread(target=show_loading_indicator, args=(stop_event,))
      
      # loading_thread.start()
      api2swagger_main(sdk_name, ["--input", requests_path, "--output", openapi_path, "--api-prefix", base_url, "--format", "flow"])
      # stop_event.set()
      # loading_thread.join()

      should_generate_sdk = input("Do you want to generate the SDK now? (y/n): ")
      if should_generate_sdk.lower() in ["y", "yes", ""]:
        # loading_thread.start()
        construct_sdk(openapi_path, sdk_name, sdk_location)
        # stop_event.set()
        # loading_thread.join()
        print("SDK generated successfully at: ", f"{sdk_location}/{sdk_name}.py")
        break
      elif should_generate_sdk.lower() in ["n", "no"]:
        break
      else:
        print("Invalid input. Please enter 'y' or 'n'.")
        continue



if __name__ == "__main__":
  main()
