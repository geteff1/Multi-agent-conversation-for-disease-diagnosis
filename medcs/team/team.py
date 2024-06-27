from metagpt.team import Team
from metagpt.logs import logger
from metagpt.utils.common import serialize_decorator


class MedTeam(Team):

    @serialize_decorator
    async def run(self, n_round=3, idea="", send_to="", auto_archive=True):
        """Run company until target round or no money"""
        # import pdb;pdb.set_trace()
        if idea:
            self.run_project(idea=idea, send_to=send_to)
        
        
        while n_round > 0:
            n_round -= 1
            self._check_balance()
            await self.env.run()

            logger.debug(f"max {n_round=} left.")
        self.env.archive(auto_archive)
        return self.env
