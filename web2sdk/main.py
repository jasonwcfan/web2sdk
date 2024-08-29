import argparse
import os
import sys
from typing import Any, Optional, Sequence, Union
from web2swagger.main import main as web2swagger_main
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
    "-a",
    "--auth-type",
    help="Auth type to determine how the SDK should handle auth. Possible values: basic, bearer, none.",
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
    if not args.requests_path or not args.sdk_name or not args.base_url or not args.auth_type:
      parser.error("--requests-path, --sdk-name, --auth-type, and --base-url are required when not running in --interactive mode.")
    if args.auth_type and args.auth_type not in ["basic", "bearer", "none"]:
      parser.error("--auth-type must be one of 'basic', 'bearer', or 'none.")
    
    openapi_path = f"{output_path}/{args.sdk_name}.yaml"
    sdk_path = f"{output_path}/{args.sdk_name}.py"
    os.makedirs(output_path, exist_ok=True)
    
    print("\n")
    web2swagger_main(args.sdk_name, ["--input", args.requests_path, "--output", openapi_path, "--api-prefix", args.base_url])
    print("OpenAPI schema generated successfully at: ", openapi_path)
    print("\n")
    construct_sdk(openapi_path, args.sdk_name, output_path, auth_type=args.auth_type, progress_callback=progress_callback)
    print(" Done!")
    sys.stdout.write(f"SDK generated successfully at: {sdk_path}")
  else:
    while True:
      requests_path = input("Enter the path to the mitmproxy dump file or HAR: ")
      base_url = input("Enter the base URL for the API (e.g. https://api.finic.ai/v1): ")
      sdk_name = input("Enter a name for the generated SDK (e.g. FinicAPI): ")
      
      use_auth = input("Does this API require authentication? (y/n): ")
      while use_auth.lower() not in ["y", "n", "yes", "no"]:
        print("Invalid input. Please enter 'y' or 'n'.")
        use_auth = input("Does this API require authentication? (y/n): ")


      if use_auth.lower() in ["y", "yes", ""]:
        auth_type = input("What type of authentication does this API use? (basic/bearer): ")
        while auth_type not in ["basic", "bearer"]:
            print("Invalid auth type. Please enter 'basic' or 'bearer'.")
            auth_type = input("What type of authentication does this API use? (basic/bearer): ")
      elif use_auth.lower() in ["n", "no"]:
        auth_type = "none"
      
      openapi_path = f"generated/{sdk_name}.yaml"
      os.makedirs("generated", exist_ok=True)
      web2swagger_main(sdk_name, ["--input", requests_path, "--output", openapi_path, "--api-prefix", base_url])
      print("OpenAPI schema generated successfully at: ", openapi_path)
      print("\n")
      construct_sdk(openapi_path, args.sdk_name, output_path, auth_type=args.auth_type, progress_callback=progress_callback)
      print(" Done!")
      sys.stdout.write(f"SDK generated successfully at: {sdk_path}")

if __name__ == "__main__":
  main()
