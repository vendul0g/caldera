#!/usr/bin/env python3

import argparse
import requests
import json
import os
import sys

# Constants
DEFAULT_API_URL = "http://localhost:8888/api/v2"
DEFAULT_API_KEY = "8wUKtFFQXgsunhsO7Q0EnKt1QCZaCZApHlbPxoXfaao"

def get_headers(api_key, content_type=None) -> dict:
    """
    Generate HTTP headers for API requests.
    Args:
        api_key (str): The API key to be included in the headers.
        content_type (str, optional): The content type to be included in the headers. Defaults to None.
    Returns:
        dict: A dictionary containing the headers with the API key and optionally the content type.
    """
    
    headers = {
        "Key": api_key,
        "Accept": "application/json"
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers

def check_health(args):
    """
    Check the health of the API by sending a GET request to the /health endpoint.
    Args:
        args: An object containing the following attributes:
            - api_url (str): The base URL of the API.
            - api_key (str): The API key for authentication.
    Prints:
        The status code of the response.
        The headers of the response.
    Raises:
        requests.exceptions.RequestException: If there is an error while making the GET request.
    """
    
    url = f"{args.api_url}/health"
    headers = get_headers(args.api_key)
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def get_agents(args):
    """
    Fetches a list of agents from the specified API URL and prints the result in a formatted JSON.
    Args:
        args: An object containing the following attributes:
            - api_url (str): The base URL of the API.
            - api_key (str): The API key for authentication.
    Raises:
        requests.exceptions.RequestException: If there is an error while making the HTTP request.
    Prints:
        A formatted JSON string of the agents if the request is successful.
        An error message if the request fails.
    """
    
    url = f"{args.api_url}/agents"
    headers = get_headers(args.api_key)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        agents = response.json()
        print(json.dumps(agents, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def get_abilities(args):
    """
    Fetches abilities from the specified API URL and prints them in a formatted JSON structure.
    Args:
        args: An object containing the following attributes:
            - api_url (str): The base URL of the API.
            - api_key (str): The API key for authentication.
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    Prints:
        A formatted JSON string of the abilities retrieved from the API.
    """
    
    url = f"{args.api_url}/abilities"
    headers = get_headers(args.api_key)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        abilities = response.json()
        print(json.dumps(abilities, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def get_parsers(args):
    """
    Fetches parsers from the specified API URL and prints them in a formatted JSON structure.
    Args:
        args: An object containing the following attributes:
            - api_url (str): The base URL of the API.
            - api_key (str): The API key for authentication.
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    Prints:
        A formatted JSON string of the parsers retrieved from the API.
    """
    
    url = f"{args.api_url}/parsers"
    headers = get_headers(args.api_key)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        parsers = response.json()
        print(json.dumps(parsers, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def create_ability(args):
    """
    Create a new ability by sending a POST request to the specified API endpoint.
    Args:
        args: An object containing the following attributes:
            - api_url (str): The base URL of the API.
            - api_key (str): The API key for authentication.
            - json_file (str): The path to the JSON file containing the ability data.
    Raises:
        SystemExit: If there is an error reading the JSON file.
        requests.exceptions.RequestException: If there is an error with the HTTP request.
    The function performs the following steps:
        1. Constructs the URL for the abilities endpoint.
        2. Loads the JSON data from the specified file.
        3. Sends a POST request to the API with the JSON data and headers.
        4. Prints the created ability in a formatted JSON structure if successful.
        5. Prints an error message and the response text if the request fails.
    """
    
    url = f"{args.api_url}/abilities"
    headers = get_headers(args.api_key, content_type="application/json")
    
    # Load JSON data from file
    try:
        with open(args.json_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        ability = response.json()
        print("Ability created successfully:")
        print(json.dumps(ability, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if response is not None:
            print("Response:", response.text)

def delete_ability(args):
    """
    Deletes an ability from the server using the provided arguments.
    Args:
        args: An object containing the following attributes:
            - ability_id (str): The ID of the ability to be deleted.
            - api_url (str): The base URL of the API.
            - api_key (str): The API key for authentication.
    Returns:
        None
    Prints:
        A success message if the ability is deleted successfully.
        An error message if the deletion fails, including the status code and response text.
        An exception message if a request exception occurs.
    """
    
    ability_id = args.ability_id
    url = f"{args.api_url}/abilities/{ability_id}"
    headers = get_headers(args.api_key)
    try:
        response = requests.delete(url, headers=headers, verify=False)  # Assuming HTTPS with self-signed cert
        if response.status_code == 204:
            print(f"Ability '{ability_id}' deleted successfully.")
        else:
            print(f"Failed to delete ability. Status Code: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        
def get_ability(args):
    """
    Fetches and prints the details of a specific ability from the API.
    Args:
        args: An object containing the following attributes:
            - ability_id (str): The ID of the ability to fetch.
            - api_url (str): The base URL of the API.
            - api_key (str): The API key for authentication.
    Raises:
        requests.exceptions.RequestException: If there is an error while making the request.
    Prints:
        The details of the ability in JSON format, indented for readability.
    """
    
    ability_id = args.ability_id
    url = f"{args.api_url}/abilities/{ability_id}"
    headers = get_headers(args.api_key)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        ability = response.json()
        print(json.dumps(ability, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Command-line tool to interact with the Caldera API."
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"Base URL for the API (default: {DEFAULT_API_URL})"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("CALDERA_API_KEY", DEFAULT_API_KEY),
        help="API key for authentication (default from environment or hardcoded)"
    )
    
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    subparsers.required = True

    ####################################################################
    ###                        HEALTH CHECK                          ###
    ####################################################################
    parser_health = subparsers.add_parser("health", help="Check API health status")
    parser_health.set_defaults(func=check_health)

    ####################################################################
    ###                            AGENTS                            ###
    ####################################################################
    parser_agents = subparsers.add_parser("get_agents", help="Retrieve list of agents")
    parser_agents.set_defaults(func=get_agents)

    ####################################################################
    ###                          ABILITIES                           ###
    ####################################################################
    # Get Abilities
    parser_abilities = subparsers.add_parser("get_abilities", help="Retrieve list of abilities")
    parser_abilities.set_defaults(func=get_abilities)
    
    # Get single Ability
    parser_ability = subparsers.add_parser("get_ability", help="Retrieve a single ability by its ID")
    parser_ability.add_argument(
        "ability_id",
        help="ID of the ability to retrieve"
    )
    parser_ability.set_defaults(func=get_ability)

    # Create Ability
    parser_create = subparsers.add_parser("create_ability", help="Create a new ability from a JSON file")
    parser_create.add_argument(
        "json_file",
        help="Path to the JSON file containing the ability definition"
    )
    parser_create.set_defaults(func=create_ability)

    # Delete Ability
    parser_delete = subparsers.add_parser("delete_ability", help="Delete an ability by its ID")
    parser_delete.add_argument(
        "ability_id",
        help="ID of the ability to delete"
    )
    parser_delete.set_defaults(func=delete_ability)

    ####################################################################
    ###                          PARSERS                             ###
    ####################################################################
    # Get Parsers
    parser_parsers = subparsers.add_parser("get_parsers", help="Retrieve list of parsers")
    parser_parsers.set_defaults(func=get_parsers)

    ####################################################################
    ###                          ADVERSARIES                         ###
    ####################################################################
    # Get Adversaries
    parser_adversaries = subparsers.add_parser("get_adversaries", help="Retrieve list of adversaries")
    parser_adversaries.set_defaults(func=get_adversaries)

    # Get single Adversary
    parser_adversary = subparsers.add_parser("get_adversary", help="Retrieve a single adversary by its ID")
    parser_adversary.add_argument(
        "adversary_id",
        help="ID of the adversary to retrieve"
    )
    parser_adversary.set_defaults(func=get_adversary)

    # Create Adversary
    parser_create_adversary = subparsers.add_parser("create_adversary", help="Create a new adversary from a JSON file")
    parser_create_adversary.add_argument(
        "json_file",
        help="Path to the JSON file containing the adversary definition"
    )
    parser_create_adversary.set_defaults(func=create_adversary)

    # Delete Adversary
    parser_delete_adversary = subparsers.add_parser("delete_adversary", help="Delete an adversary by its ID")
    parser_delete_adversary.add_argument(
        "adversary_id",
        help="ID of the adversary to delete"
    )
    parser_delete_adversary.set_defaults(func=delete_adversary)
    
    ########################### END OF ARGS ###########################
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    # Disable SSL warnings if needed (e.g., self-signed certificates)
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    main()
