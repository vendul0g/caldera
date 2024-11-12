#!/usr/bin/env python3

import argparse
import requests
import json
import os
import sys

# Constants
DEFAULT_API_URL = "http://localhost:8888/api/v2"
DEFAULT_API_KEY = "8wUKtFFQXgsunhsO7Q0EnKt1QCZaCZApHlbPxoXfaao"

def get_headers(api_key, content_type=None):
    headers = {
        "Key": api_key,
        "Accept": "application/json"
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers

def check_health(args):
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

    # Health
    parser_health = subparsers.add_parser("health", help="Check API health status")
    parser_health.set_defaults(func=check_health)

    # Get Agents
    parser_agents = subparsers.add_parser("get_agents", help="Retrieve list of agents")
    parser_agents.set_defaults(func=get_agents)

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

    # Get Parsers
    parser_parsers = subparsers.add_parser("get_parsers", help="Retrieve list of parsers")
    parser_parsers.set_defaults(func=get_parsers)

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

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    # Disable SSL warnings if needed (e.g., self-signed certificates)
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    main()
