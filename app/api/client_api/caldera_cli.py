#!/usr/bin/env python3

import argparse
import requests
import json
import os
import sys
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Constants
DEFAULT_API_URL = os.getenv("API_URL", "http://localhost:8888/api/v2")
DEFAULT_API_KEY = os.getenv("API_KEY")


class APIClient:
    """
    A client for interacting with the Caldera API.
    """

    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the API client with the base URL and API key.

        Args:
            api_url (str): The base URL of the API.
            api_key (str): The API key for authentication.
        """
        self.api_url = api_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Key": self.api_key, "Accept": "application/json"})

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Send a GET request to the API.

        Args:
            endpoint (str): The API endpoint to send the request to.
            params (dict, optional): Query parameters for the request.

        Returns:
            The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        url = f"{self.api_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            logger.debug(f"GET {url} - Status Code: {response.status_code}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GET {url} failed: {e}")
            raise

    def post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """
        Send a POST request to the API.

        Args:
            endpoint (str): The API endpoint to send the request to.
            data (dict): The JSON data to send in the request body.

        Returns:
            The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        url = f"{self.api_url}/{endpoint}"
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            logger.debug(f"POST {url} - Status Code: {response.status_code}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"POST {url} failed: {e}")
            raise

    def delete(self, endpoint: str) -> None:
        """
        Send a DELETE request to the API.

        Args:
            endpoint (str): The API endpoint to send the request to.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        url = f"{self.api_url}/{endpoint}"
        try:
            response = self.session.delete(url, verify=False)  # Adjust verify as needed
            response.raise_for_status()
            logger.debug(f"DELETE {url} - Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"DELETE {url} failed: {e}")
            raise

    def patch(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """
        Send a PATCH request to the API.

        Args:
            endpoint (str): The API endpoint to send the request to.
            data (dict): The JSON data to send in the request body.

        Returns:
            The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        url = f"{self.api_url}/{endpoint}"
        try:
            response = self.session.patch(url, json=data)
            response.raise_for_status()
            logger.debug(f"PATCH {url} - Status Code: {response.status_code}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"PATCH {url} failed: {e}")
            raise

    # Aquí podemos añadir más métodos cuando llegue a eso


"""================================================================="""
"""                          Health Check                           """
"""================================================================="""


def check_health(client: APIClient, args: argparse.Namespace) -> None:
    """
    Check the health of the API.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        health = client.get("health")
        logger.info("API Health:")
        print(json.dumps(health, indent=2))
    except Exception as e:
        logger.error(f"Health check failed: {e}")


"""================================================================="""
"""                            Agents                               """
"""================================================================="""


def get_agents(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a list of agents.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        agents = client.get("agents")
        logger.info("Agents:")
        print(json.dumps(agents, indent=2))
    except Exception as e:
        logger.error(f"Failed to get agents: {e}")


def get_agents_paw(client: APIClient, args: argparse.Namespace) -> None:
    """
    Get the list of agents paw.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        agents = client.get("agents")
        logger.info("List of agents (ID and paw):")

        for agent in agents:
            for link in agent.get("links", []):
                agent_id = link.get("id")
                agent_paw = agent.get("paw")
                print(f"ID: {agent_id}, Paw: {agent_paw}")

    except Exception as e:
        logger.error(f"Failed to get agents: {e}")


"""================================================================="""
"""                          Abilities                              """
"""================================================================="""


def get_abilities(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a list of abilities.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        abilities = client.get("abilities")
        logger.info("Abilities:")
        print(json.dumps(abilities, indent=2))
    except Exception as e:
        logger.error(f"Failed to get abilities: {e}")


def create_ability(client: APIClient, args: argparse.Namespace) -> None:
    """
    Create a new ability from a JSON file.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        with open(args.json_file, "r") as f:
            data = json.load(f)
        ability = client.post("abilities", data)
        logger.info("Ability created successfully:")
        print(json.dumps(ability, indent=2))
    except Exception as e:
        logger.error(f"Failed to create ability: {e}")


def get_ability(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a single ability by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        ability = client.get(f"abilities/{args.ability_id}")
        logger.info(f"Ability '{args.ability_id}':")
        print(json.dumps(ability, indent=2))
    except Exception as e:
        logger.error(f"Failed to get ability: {e}")


def delete_ability(client: APIClient, args: argparse.Namespace) -> None:
    """
    Delete an ability by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        client.delete(f"abilities/{args.ability_id}")
        logger.info(f"Ability '{args.ability_id}' deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete ability: {e}")


def update_ability(client: APIClient, args: argparse.Namespace) -> None:
    """
    Update an ability by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        with open(args.json_file, "r") as f:
            data = json.load(f)
        ability = client.patch(f"abilities/{args.ability_id}", data)
        logger.info(f"Ability '{args.ability_id}' updated successfully:")
        print(json.dumps(ability, indent=2))
    except Exception as e:
        logger.error(f"Failed to update ability: {e}")


def create_manual_command(client: Any, args: Any) -> None:
    """
    Execute a manual command on an agent of an already running operation.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments containing:
            - operation_id (str): ID of the operation to target.
            - agent_paw (str): Paw of the target agent.
            - command (str): Command to execute on the agent.
    """
    try:
        # Construct the payload for the manual command
        payload = {
            "executor": {
                "name": "proc",
                "command": args.command,
                "platform": "linux",
            },
            "paw": args.agent_paw,
        }
        # Send the POST request to the API client
        manual_command = client.post(
            f"operations/{args.operation_id}/potential-links", payload
        )
        # Log success and output the response
        logger.info(
            f"Command '{args.command}' successfully sent to agent '{args.agent_paw}'."
        )
        print(json.dumps(manual_command, indent=2))
    except Exception as e:
        logger.error(f"Failed to create manual command: {e}")


def create_manual_ability(client: Any, args: Any) -> None:
    """
    Execute a manual ability on an agent in an existing operation.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments containing:
            - operation_id (str): ID of the operation to target.
            - agent_paw (str): Paw of the target agent.
            - ability_id (str): ID of the ability to execute
    """
    try:
        # Read the JSON file
        with open(args.json_file, "r") as f:
            data = json.load(f)
        # Send the POST request to the API client
        manual_command = client.post(
            f"operations/{args.operation_id}/potential-links", data
        )
        # Log success and output the response
        logger.info(f"Ability successfully sent to agent '{args.agent_paw}'.")
        print(json.dumps(manual_command, indent=2))
    except Exception as e:
        logger.error(f"Failed to create manual ability: {e}")


"""================================================================="""
"""                            Parsers                              """
"""================================================================="""


def get_parsers(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a list of parsers.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        parsers = client.get("parsers")
        logger.info("Parsers:")
        print(json.dumps(parsers, indent=2))
    except Exception as e:
        logger.error(f"Failed to get parsers: {e}")


"""================================================================="""
"""                          Adversaries                            """
"""================================================================="""


def get_adversaries(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a list of adversaries.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        adversaries = client.get("adversaries")
        logger.info("Adversaries:")
        print(json.dumps(adversaries, indent=2))
    except Exception as e:
        logger.error(f"Failed to get adversaries: {e}")


def get_adversary(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a single adversary by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        adversary = client.get(f"adversaries/{args.adversary_id}")
        logger.info(f"Adversary '{args.adversary_id}':")
        print(json.dumps(adversary, indent=2))
    except Exception as e:
        logger.error(f"Failed to get adversary: {e}")


def create_adversary(client: APIClient, args: argparse.Namespace) -> None:
    """
    Create a new adversary from a JSON file.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        with open(args.json_file, "r") as f:
            data = json.load(f)
        adversary = client.post("adversaries", data)
        logger.info("Adversary created successfully:")
        print(json.dumps(adversary, indent=2))
    except Exception as e:
        logger.error(f"Failed to create adversary: {e}")


def delete_adversary(client: APIClient, args: argparse.Namespace) -> None:
    """
    Delete an adversary by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        client.delete(f"adversaries/{args.adversary_id}")
        logger.info(f"Adversary '{args.adversary_id}' deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete adversary: {e}")


def update_adversary(client: APIClient, args: argparse.Namespace) -> None:
    """
    Update and adversary by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        with open(args.json_file, "r") as f:
            data = json.load(f)
        adversary = client.patch(f"adversaries/{args.adversary_id}", data)
        logger.info("Adversary updated successfully")
        print(json.dumps(adversary, indent=2))
    except Exception as e:
        logger.error(f"Failed to create adversary: {e}")


"""================================================================="""
"""                          Operations                             """
"""================================================================="""


def get_operations(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a list of operations.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        operations = client.get("operations")
        logger.info("Operations:")
        print(json.dumps(operations, indent=2))
    except Exception as e:
        logger.error(f"Failed to get operations: {e}")


def create_operation(client: APIClient, args: argparse.Namespace) -> None:
    """
    Create a new operation from a JSON file.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        with open(args.json_file, "r") as f:
            data = json.load(f)
        operation = client.post("operations", data)
        logger.info("Operation created successfully:")
        print(json.dumps(operation, indent=2))
    except Exception as e:
        logger.error(f"Failed to create operation: {e}")


def get_operation(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a single operation by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        operation = client.get(f"operations/{args.operation_id}")
        logger.info(f"Operation '{args.operation_id}':")
        print(json.dumps(operation, indent=2))
    except Exception as e:
        logger.error(f"Failed to get operation: {e}")


def delete_operation(client: APIClient, args: argparse.Namespace) -> None:
    """
    Delete an operation by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        client.delete(f"operations/{args.operation_id}")
        logger.info(f"Operation '{args.operation_id}' deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete operation: {e}")


def get_operation_report(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a report for a specific operation.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        report = client.post(
            f"operations/{args.operation_id}/report", {"enable_agent_output": True}
        )
        logger.info(f"Report for operation '{args.operation_id}':")
        print(json.dumps(report, indent=2))
    except Exception as e:
        logger.error(f"Failed to get operation report: {e}")


def get_operation_event_logs(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve event logs for a specific operation.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        event_logs = client.post(
            f"operations/{args.operation_id}/event-logs", {"enable_agent_output": True}
        )
        logger.info(f"Event logs for operation '{args.operation_id}':")
        print(json.dumps(event_logs, indent=2))
    except Exception as e:
        logger.error(f"Failed to get operation event logs: {e}")


def get_operation_links(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve links for a specific operation.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        links = client.get(f"operations/{args.operation_id}/links")
        logger.info(f"Links for operation '{args.operation_id}':")
        print(json.dumps(links, indent=2))
    except Exception as e:
        logger.error(f"Failed to get operation links: {e}")


def create_operation_command(client: APIClient, args: argparse.Namespace) -> None:
    """
    Create a new command for a specific operation.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        with open(args.json_file, "r") as f:
            data = json.load(f)
        command = client.post(f"operations/{args.operation_id}/potential-links", data)
        logger.info("Command created successfully:")
        print(json.dumps(command, indent=2))
    except Exception as e:
        logger.error(f"Failed to create command: {e}")


"""================================================================="""
"""                           Scheduler                             """
"""================================================================="""


def get_schedules(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve Schedules.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        schedules = client.get("schedules")
        logger.info("Schedules:")
        print(json.dumps(schedules, indent=2))
    except Exception as e:
        logger.error(f"Failed to get schedules: {e}")


def create_schedule(client: APIClient, args: argparse.Namespace) -> None:
    """
    Create a new Schedule from a JSON file.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        with open(args.json_file, "r") as f:
            data = json.load(f)
        schedule = client.post("schedules", data)
        logger.info("Schedule created successfully:")
        print(json.dumps(schedule, indent=2))
    except Exception as e:
        logger.error(f"Failed to create schedule: {e}")


def get_schedule(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a single Schedule by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        schedule = client.get(f"schedules/{args.schedule_id}")
        logger.info(f"Schedule '{args.schedule_id}':")
        print(json.dumps(schedule, indent=2))
    except Exception as e:
        logger.error(f"Failed to get schedule: {e}")


def delete_schedule(client: APIClient, args: argparse.Namespace) -> None:
    """
    Delete a Schedule by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        client.delete(f"schedules/{args.schedule_id}")
        logger.info(f"Schedule '{args.schedule_id}' deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete schedule: {e}")


"""================================================================="""
"""                           Planners                              """
"""================================================================="""


def get_planners(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve planners.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        planners = client.get("planners")
        logger.info("Planners:")
        print(json.dumps(planners, indent=2))
    except Exception as e:
        logger.error(f"Failed to get planners: {e}")


def get_planner(client: APIClient, args: argparse.Namespace) -> None:
    """
    Retrieve a single planner by its ID.

    Args:
        client (APIClient): The API client instance.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    try:
        planner = client.get(f"planners/{args.planner_id}")
        logger.info(f"Planner '{args.planner_id}':")
        print(json.dumps(planner, indent=2))
    except Exception as e:
        logger.error(f"Failed to get planner: {e}")

"""================================================================="""
"""============                 Main                 ==============="""
"""================================================================="""


def main():
    parser = argparse.ArgumentParser(
        description="Command-line tool to interact with the Caldera API."
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"Base URL for the API (default: {DEFAULT_API_URL})",
    )
    parser.add_argument(
        "--api-key",
        default=DEFAULT_API_KEY,
        help="API key for authentication (default from environment variable API_KEY)",
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
    # Get agents JSON
    parser_agents = subparsers.add_parser("get_agents", help="Retrieve list of agents")
    parser_agents.set_defaults(func=get_agents)

    # Get Agents paw
    parser_agents_paw = subparsers.add_parser(
        "get_agents_paw", help="Get the list of agents paw"
    )
    parser_agents_paw.set_defaults(func=get_agents_paw)

    ####################################################################
    ###                          ABILITIES                           ###
    ####################################################################
    # Get Abilities
    parser_abilities = subparsers.add_parser(
        "get_abilities", help="Retrieve list of abilities"
    )
    parser_abilities.set_defaults(func=get_abilities)

    # Get single Ability
    parser_ability = subparsers.add_parser(
        "get_ability", help="Retrieve a single ability by its ID"
    )
    parser_ability.add_argument("ability_id", help="ID of the ability to retrieve")
    parser_ability.set_defaults(func=get_ability)

    # Create Ability
    parser_create = subparsers.add_parser(
        "create_ability", help="Create a new ability from a JSON file"
    )
    parser_create.add_argument(
        "json_file", help="Path to the JSON file containing the ability definition"
    )
    parser_create.set_defaults(func=create_ability)

    # Delete Ability
    parser_delete = subparsers.add_parser(
        "delete_ability", help="Delete an ability by its ID"
    )
    parser_delete.add_argument("ability_id", help="ID of the ability to delete")
    parser_delete.set_defaults(func=delete_ability)

    # Update Ability
    parser_update_ability = subparsers.add_parser(
        "update_ability", help="Update an ability by its ID"
    )
    parser_update_ability.add_argument("ability_id", help="ID of the ability to delete")
    parser_update_ability.add_argument(
        "json_file", help="Path to the JSON file containing the ability definition"
    )
    parser_update_ability.set_defaults(func=update_ability)

    # Create Manual Command into an Operation
    parser_manual_command = subparsers.add_parser(
        "create_manual_command",
        help="Create a Manual command into an Agent inside an Operation",
    )
    parser_manual_command.add_argument("operation_id", help="ID of the operation")
    parser_manual_command.add_argument(
        "agent_paw", help="Paw of the agent where the command would be executed"
    )
    parser_manual_command.add_argument(
        "command", help="The command to be executed on the agent"
    )
    parser_manual_command.set_defaults(func=create_manual_command)

    # Create manual Ability into an Operation
    parser_manual_ability = subparsers.add_parser(
        "create_manual_ability",
        help="Create a Manual Ability into an Agent inside an Operation",
    )
    parser_manual_ability.add_argument("operation_id", help="ID of the operation")
    parser_manual_ability.add_argument(
        "agent_paw", help="Paw of the agent where the ability would be executed"
    )
    parser_manual_ability.add_argument(
        "json_file", help="Path to the JSON file where ability is described"
    )
    parser_manual_ability.set_defaults(func=create_manual_ability)

    ####################################################################
    ###                          PARSERS                             ###
    ####################################################################
    # Get Parsers
    parser_parsers = subparsers.add_parser(
        "get_parsers", help="Retrieve list of parsers"
    )
    parser_parsers.set_defaults(func=get_parsers)

    ####################################################################
    ###                          ADVERSARIES                         ###
    ####################################################################
    # Get Adversaries
    parser_adversaries = subparsers.add_parser(
        "get_adversaries", help="Retrieve list of adversaries"
    )
    parser_adversaries.set_defaults(func=get_adversaries)

    # Get single Adversary
    parser_adversary = subparsers.add_parser(
        "get_adversary", help="Retrieve a single adversary by its ID"
    )
    parser_adversary.add_argument(
        "adversary_id", help="ID of the adversary to retrieve"
    )
    parser_adversary.set_defaults(func=get_adversary)

    # Create Adversary
    parser_create_adversary = subparsers.add_parser(
        "create_adversary", help="Create a new adversary from a JSON file"
    )
    parser_create_adversary.add_argument(
        "json_file", help="Path to the JSON file containing the adversary definition"
    )
    parser_create_adversary.set_defaults(func=create_adversary)

    # Delete Adversary
    parser_delete_adversary = subparsers.add_parser(
        "delete_adversary", help="Delete an adversary by its ID"
    )
    parser_delete_adversary.add_argument(
        "adversary_id", help="ID of the adversary to delete"
    )
    parser_delete_adversary.set_defaults(func=delete_adversary)

    # Update Adversary
    parser_update_adversary = subparsers.add_parser(
        "update_adversary", help="Update an adversary by its ID"
    )
    parser_update_adversary.add_argument(
        "adversary_id", help="ID of the adversary to delete"
    )
    parser_update_adversary.add_argument(
        "json_file", help="Path to the JSON file containing the adversary definition"
    )
    parser_update_adversary.set_defaults(func=update_adversary)

    ####################################################################
    ###                          OPERATIONS                          ###
    ####################################################################
    # Get Operations
    parser_operations = subparsers.add_parser(
        "get_operations", help="Retrieve list of operations"
    )
    parser_operations.set_defaults(func=get_operations)

    # Get single Operation
    parser_operation = subparsers.add_parser(
        "get_operation", help="Retrieve a single operation by its ID"
    )
    parser_operation.add_argument(
        "operation_id", help="ID of the operation to retrieve"
    )
    parser_operation.set_defaults(func=get_operation)

    # Create Operation
    parser_create_operation = subparsers.add_parser(
        "create_operation", help="Create a new operation from a JSON file"
    )
    parser_create_operation.add_argument(
        "json_file", help="Path to the JSON file containing the operation definition"
    )
    parser_create_operation.set_defaults(func=create_operation)

    # Delete Operation
    parser_delete_operation = subparsers.add_parser(
        "delete_operation", help="Delete an operation by its ID"
    )
    parser_delete_operation.add_argument(
        "operation_id", help="ID of the operation to delete"
    )
    parser_delete_operation.set_defaults(func=delete_operation)

    # Get Operation report
    parser_operation_report = subparsers.add_parser(
        "get_operation_report",
        help="Retrieve a report for a specific operation: global information and details",
    )
    parser_operation_report.add_argument(
        "operation_id", help="ID of the operation to retrieve the report for"
    )
    parser_operation_report.set_defaults(func=get_operation_report)

    # Get Operation Event Logs
    parser_operation_event_logs = subparsers.add_parser(
        "get_operation_event_logs",
        help="Retrieve event logs for a specific operation: detailed information about the operation's execution",
    )
    parser_operation_event_logs.add_argument(
        "operation_id", help="ID of the operation to retrieve event logs for"
    )
    parser_operation_event_logs.set_defaults(func=get_operation_event_logs)

    # Get Operation Links
    parser_operation_links = subparsers.add_parser(
        "get_operation_links", help="Get Links for a specific operation"
    )
    parser_operation_links.add_argument(
        "operation_id", help="ID of the operation to retrieve links for"
    )
    parser_operation_links.set_defaults(func=get_operation_links)

    ####################################################################
    ###                           SCHEDULER                          ###
    ####################################################################
    # Get Schedules
    parser_schedules = subparsers.add_parser(
        "get_schedules", help="Retrieve Schedulesdules"
    )
    parser_schedules.set_defaults(func=get_schedules)

    # Create Schedule
    parser_create_schedule = subparsers.add_parser(
        "create_schedule", help="Create a new Schedule from a JSON file"
    )
    parser_create_schedule.add_argument(
        "json_file", help="Path to the JSON file containing the Schedule definition"
    )
    parser_create_schedule.set_defaults(func=create_schedule)

    # Get single Schedule
    parser_schedule = subparsers.add_parser(
        "get_schedule", help="Retrieve a single Schedule by its ID"
    )
    parser_schedule.add_argument("schedule_id", help="ID of the Schedule to retrieve")
    parser_schedule.set_defaults(func=get_schedule)

    # Delete Schedule
    parser_delete_schedule = subparsers.add_parser(
        "delete_schedule", help="Delete a Schedule by its ID"
    )
    parser_delete_schedule.add_argument(
        "schedule_id", help="ID of the Schedule to delete"
    )
    parser_delete_schedule.set_defaults(func=delete_schedule)

    ####################################################################
    ###                           PLANNERS                           ###
    ####################################################################
    # Get Planners
    parser_get_planners = subparsers.add_parser(
        "get_planners", help="Get the planners of Caldera"
    )
    parser_get_planners.set_defaults(func=get_planners)
    
    # Get single planner
    parser_planner = subparsers.add_parser(
        "get_planner", help="Retrieve a single planner by its ID"
    )
    parser_planner.add_argument("planner_id", help="ID of the planner to retrieve")
    parser_planner.set_defaults(func=get_planner)

    ########################### END OF ARGS ###########################
    args = parser.parse_args()

    # Check for API key
    if not args.api_key:
        logger.error(
            "API key is required. Please set the API_KEY environment variable or use the --api-key argument."
        )
        sys.exit(1)

    # Initialize the API client
    client = APIClient(api_url=args.api_url, api_key=args.api_key)

    # Execute the selected command
    args.func(client, args)


if __name__ == "__main__":
    # Disable SSL warnings if needed (e.g., self-signed certificates)
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning
    )
    main()
