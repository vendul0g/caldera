import os
import logging
import aiohttp_apispec
from aiohttp import web

from app.api.v2.handlers.base_object_api import BaseObjectApi
from app.api.v2.managers.base_api_manager import BaseApiManager
from app.api.v2.schemas.base_schemas import BaseGetAllQuerySchema, BaseGetOneQuerySchema
from app.objects.c_planner import Planner, PlannerSchema
import yaml


class PlannerApi(BaseObjectApi):
    def __init__(self, services):
        super().__init__(
            description="planner",
            obj_class=Planner,
            schema=PlannerSchema,
            ram_key="planners",
            id_property="planner_id",
            auth_svc=services["auth_svc"],
        )
        self._data_svc = services["data_svc"]
        self._file_svc = services["file_svc"]
        self._api_manager = BaseApiManager(
            data_svc=self._data_svc, file_svc=self._file_svc
        )

    def add_routes(self, app: web.Application):
        router = app.router
        router.add_get("/planners", self.get_planners)
        router.add_get("/planners/{planner_id}", self.get_planner_by_id)
        router.add_patch("/planners/{planner_id}", self.update_planner)
        router.add_delete("/planners/{planner_id}", self.delete_planner)

    @aiohttp_apispec.docs(
        tags=["planners"],
        summary="Retrieve planners",
        description="Retrieve Caldera planners by criteria. Supply fields from the `PlannerSchema` "
        "to the `include` and `exclude` fields of the `BaseGetAllQuerySchema` in the "
        "request body to filter retrieved planners.",
    )
    @aiohttp_apispec.querystring_schema(BaseGetAllQuerySchema)
    @aiohttp_apispec.response_schema(
        PlannerSchema(many=True, partial=True),
        description="Returns a list of matching planners in `PlannerSchema` format.",
    )
    async def get_planners(self, request: web.Request):
        planners = await self.get_all_objects(request)
        return web.json_response(planners)

    @aiohttp_apispec.docs(
        tags=["planners"],
        summary="Retrieve a planner by planner id",
        description="Retrieve one Caldera planner based on the planner id (String `UUID`). "
        "Supply fields from the `PlannerSchema` to the `include` and `exclude` fields "
        "of the `BaseGetOneQuerySchema` in the request body to filter retrieved "
        "planners.",
        parameters=[
            {
                "in": "path",
                "name": "planner_id",
                "schema": {"type": "string"},
                "required": "true",
                "description": "UUID of the Planner object to be retrieved.",
            }
        ],
    )
    @aiohttp_apispec.querystring_schema(BaseGetOneQuerySchema)
    @aiohttp_apispec.response_schema(
        PlannerSchema(partial=True),
        description="Returns a planner with the specified id in `PlannerSchema` format.",
    )
    async def get_planner_by_id(self, request: web.Request):
        planner = await self.get_object(request)
        return web.json_response(planner)

    @aiohttp_apispec.docs(
        tags=["planners"],
        summary="Updates an existing planner.",
        description="Updates a planner based on the `PlannerSchema` value provided in the message body.",
        parameters=[
            {
                "in": "path",
                "name": "planner_id",
                "schema": {"type": "string"},
                "required": "true",
                "description": "UUID of the Planner to be updated",
            }
        ],
    )
    @aiohttp_apispec.request_schema(PlannerSchema(partial=True))
    @aiohttp_apispec.response_schema(
        PlannerSchema(partial=True),
        description="JSON dictionary representation of the replaced Planner.",
    )
    async def update_planner(self, request: web.Request):
        planner = await self.update_on_disk_object(request)
        return web.json_response(planner.display)

    @aiohttp_apispec.docs(
        tags=["planners"],
        summary="Delete a planner",
        description="Deletes a planner based on the planner_id provided in the path.",
        parameters=[
            {
                "in": "path",
                "name": "planner_id",
                "schema": {"type": "string"},
                "required": True,
                "description": "UUID of the Planner to be deleted.",
            }
        ],
    )
    @aiohttp_apispec.response_schema(None, description="Planner deleted successfully.")
    async def delete_planner(self, request: web.Request):
        try:
            # Get the planner_id from request
            planner_id = request.match_info.get(self.id_property)
            logging.debug(f"Received planner ID: {planner_id}")

            if not planner_id:
                logging.error("Planner ID not provided in the request.")
                raise web.HTTPBadRequest(reason="Planner ID is required.")

            # Search planner in ram['planners']
            logging.debug("Searching for the planner in ram['planners']")
            planner = next(
                (
                    p
                    for p in self._data_svc.ram["planners"]
                    if p.planner_id == planner_id
                ),
                None,
            )
            if not planner:
                logging.debug(f"Planner with ID {planner_id} not found")
                raise web.HTTPNotFound(reason=f"Planner with ID {planner_id} not found")
            logging.debug(f"Found planner: {planner.name}")

            # Delete planner from ram['planners']
            logging.debug(f"Removing planner {planner.name} from ram['planners']")
            self._data_svc.ram["planners"].remove(planner)

            # Delete planner YAML file from disk
            file_name = f"{planner_id}.yml"
            logging.debug(f"Looking for planner YAML file: {file_name}")

            # Use file_svc to find out the YAML file path
            _, file_path = await self._file_svc.find_file_path(file_name, "planners")
            logging.debug(f"Resolved file path: {file_path}")

            if file_path and os.path.exists(file_path):
                logging.debug(f"File found. Deleting file: {file_path}")
            elif not file_path:
                # Fallback to default data/planners directory
                fallback_dir = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "../../../../data/planners"
                )
                file_path = os.path.join(fallback_dir, file_name)
                logging.debug(f"Fallback file path: {file_path}")
                if os.path.exists(file_path):
                    logging.debug(f"File found in fallback directory. Deleting file: {file_path}")
                else:
                    logging.debug(f"File not found in fallback directory: {file_path}")
                    file_path = None

            if file_path and os.path.exists(file_path):
                # Read the planner YAML file to get the module name
                with open(file_path, "r") as yaml_file:
                    planner_data = yaml.safe_load(yaml_file)
                module_name = planner_data.get("module")
                if module_name:
                    # Define possible base directories
                    base_dirs = [
                        os.path.join(
                            os.path.dirname(os.path.abspath(__file__)), "../../../../"
                        ),
                        os.path.join(
                            os.path.dirname(os.path.abspath(__file__)),
                            "../../../../plugins/stockpile/app",
                        ),
                        os.path.join(
                            os.path.dirname(os.path.abspath(__file__)),
                            "../../../../plugins/stockpile/app/planners",
                        ),
                        os.path.join(
                            os.path.dirname(os.path.abspath(__file__)),
                            "../../../../app/planners",
                        ),
                    ]
                    module_path = module_name.replace(".", os.sep) + ".py"
                    module_file_path = None
                    for base_dir in base_dirs:
                        potential_path = os.path.join(base_dir, module_path)
                        logging.debug(f"Checking for module file at: {potential_path}")
                        if os.path.exists(potential_path):
                            module_file_path = potential_path
                            break
                    if module_file_path:
                        logging.debug(f"Deleting module file: {module_file_path}")
                        os.remove(module_file_path)
                    else:
                        logging.debug(
                            f"Module file for {module_name} not found in specified directories."
                        )
                else:
                    logging.debug(
                        f"No module specified in planner YAML for planner {planner_id}"
                    )
                # Delete the planner YAML file
                os.remove(file_path)
            else:
                logging.debug(
                    f"File not found for planner {planner_id} at: {file_path}"
                )

            # Save the updated state
            logging.debug("Saving the updated state")
            await self._data_svc.save_state()

            logging.debug(f"Planner {planner.name} deleted successfully")
            return web.json_response(
                {
                    "status": "success",
                    "message": f"Planner {planner.name} deleted successfully",
                }
            )
        except web.HTTPException as http_exc:
            # Re-raise any HTTP exceptions
            raise http_exc
        except Exception as e:
            # Register any other exception and raise an internal server error
            logging.error(f"Error deleting planner: {e}", exc_info=True)
            raise web.HTTPInternalServerError(
                reason="An error occurred while deleting the planner."
            )
