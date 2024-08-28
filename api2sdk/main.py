import argparse
import os
import sys
from typing import Any, Optional, Sequence, Union
from api2swagger.main import main as api2swagger_main
from swagger2sdk.main import construct_sdk
import console_util

def progress_callback(progress):
    console_util.print_progress_bar(progress, "Generating SDK...           ")

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

  parser.add_argument(
    "-o",
    "--output",
    help="Path to the directory where generated files should be saved",
    default="generated",
    required=False,
  )

  args = parser.parse_args()
  output_path = args.output.rstrip("/")

  if not args.interactive:
    if not args.requests_path or not args.sdk_name or not args.base_url:
      parser.error("--requests-path, --sdk-name, and --base-url are required when not running in --interactive mode.")
    
    openapi_path = f"{output_path}/{args.sdk_name}.yaml"
    sdk_path = f"{output_path}/{args.sdk_name}.py"
    os.makedirs(output_path, exist_ok=True)
    
    print("\n")
    api2swagger_main(args.sdk_name, ["--input", args.requests_path, "--output", openapi_path, "--api-prefix", args.base_url])
    print("OpenAPI schema generated successfully at: ", openapi_path)
    print("\n")
    construct_sdk(openapi_path, args.sdk_name, output_path, progress_callback=progress_callback)
    print(" Done!")
    sys.stdout.write(f"SDK generated successfully at: {sdk_path}")
  else:
    while True:
      requests_path = input("Enter the path to the mitmproxy dump file or HAR: ")
      base_url = input("Enter the base URL for the API (e.g. https://api.finic.ai/v1): ")
      sdk_name = input("Enter a name for the generated SDK (e.g. FinicAPI): ")
      openapi_path = f"generated/{sdk_name}.yaml"
      os.makedirs("generated", exist_ok=True)
      api2swagger_main(sdk_name, ["--input", requests_path, "--output", openapi_path, "--api-prefix", base_url])
      print("OpenAPI schema generated successfully at: ", openapi_path)
      
      should_generate_sdk = input("Do you want to generate the SDK now? (y/n): ")
      if should_generate_sdk.lower() in ["y", "yes", ""]:
        construct_sdk(openapi_path, sdk_name, "generated", progress_callback=progress_callback)
        print("SDK generated successfully at: ", f"generated/{sdk_name}.py")
        break
      elif should_generate_sdk.lower() in ["n", "no"]:
        break
      else:
        print("Invalid input. Please enter 'y' or 'n'.")
        continue

if __name__ == "__main__":
  main()
