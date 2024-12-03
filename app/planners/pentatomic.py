import logging

class LogicalPlanner:

    def __init__(self, operation, planning_svc, stopping_conditions=()):
        self.operation = operation
        self.planning_svc = planning_svc
        self.stopping_conditions = stopping_conditions
        self.stopping_condition_met = False
        self.state_machine = ['pentatomic']
        self.next_bucket = 'pentatomic'   # Repeat this bucket until we run out of links.

        # Initialize per-agent step index
        self.agent_steps = {agent.paw: 0 for agent in self.operation.agents}

        # Set up logging
        self.logger = logging.getLogger('pentatomic_planner')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    async def execute(self):
        self.logger.debug("Executing pentatomic planner")
        await self.planning_svc.execute_planner(self)

    async def pentatomic(self):
        self.logger.debug("Entering pentatomic bucket")
        links_to_use = []

        # For each agent, get the next available link
        for agent in self.operation.agents:
            possible_agent_links = await self._get_links(agent=agent)
            step = self.agent_steps.get(agent.paw, 0)
            next_link = await self._get_next_atomic_link(possible_agent_links, agent, step)
            if next_link:
                applied_link_id = await self.operation.apply(next_link)
                links_to_use.append(applied_link_id)
                self.logger.debug(f"Applied link {applied_link_id} for agent {agent.paw}")
                # Increment the agent's step index
                self.agent_steps[agent.paw] = step + 1
            else:
                self.logger.debug(f"No more links to run for agent {agent.paw}")
                # Remove agent from tracking if no more steps
                self.agent_steps.pop(agent.paw, None)

        if links_to_use:
            # Wait for all applied links to complete
            await self.operation.wait_for_links_completion(links_to_use)
            self.logger.debug("Completed execution of links")
        else:
            # No more links to run.
            self.logger.debug("No more links to run, ending planner")
            self.next_bucket = None

    async def _get_links(self, agent=None):
        self.logger.debug(f"Getting available links for agent {agent.paw}")
        links = await self.planning_svc.get_links(operation=self.operation, agent=agent)
        self.logger.debug(f"Found {len(links)} links for agent {agent.paw}")
        return links

    # Returns the next link based on the adversary's atomic ordering and the current step
    async def _get_next_atomic_link(self, links, agent, step):
        abil_id_to_link = {link.ability.ability_id: link for link in links}
        candidate_ids = set(abil_id_to_link.keys())

        if step >= len(self.operation.adversary.atomic_ordering):
            self.logger.debug(f"Agent {agent.paw} has completed all steps")
            return None

        ab_id = self.operation.adversary.atomic_ordering[step]
        if ab_id in candidate_ids:
            self.logger.debug(f"Next ability ID for execution: {ab_id}")
            return abil_id_to_link[ab_id]
        else:
            # Ability not available, skip to next step
            self.logger.debug(f"Ability {ab_id} not available for agent {agent.paw}, skipping to next step")
            # Increment step and try again
            self.agent_steps[agent.paw] = step + 1
            return await self._get_next_atomic_link(links, agent, step + 1)
