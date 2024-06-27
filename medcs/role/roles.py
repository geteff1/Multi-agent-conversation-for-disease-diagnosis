import asyncio
import re

from enum import Enum
from pydantic import Field, SerializeAsAny, model_validator

from metagpt.roles import Role
from metagpt.logs import logger
from metagpt.schema import Message
from metagpt.actions import UserRequirement
from metagpt.utils.common import any_to_str

from medcs.action import (
    Query,
    Analysis,
    Vote,
    Correct,
    SynthesizingReport,
    Revise,
)


def cleansing_voting(output):
    output = output.lower()
    ans = re.findall(r"yes|no", output)
    if len(ans) == 0:
        ans = "yes"
    else:
        ans = ans[0]
    return ans


class Moderator(Role):
    name: str = "Moderator"
    profile: str = "Moderator"
    num_specialists: int = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _act(self) -> Message:
        todo = self.rc.todo
        logger.info(f"{self._setting}: to do {todo}({todo.name})")

        msg = self.get_memories(k=1)[0]  # find the most recent messages

        if self.name == "Selector":
            content = await todo.run(msg=msg, num_specialists=self.num_specialists)
        else:
            content = await todo.run(msg=msg)

        # logger.info(f'{selection}')
        msg = Message(content=content, role=self.profile, cause_by=type(todo))

        return msg


class Revisor(Role):
    name: str = "Revisor"
    profile: str = "Revisor"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _act(self) -> Message:
        todo = self.rc.todo
        logger.info(f"{self._setting}: to do {todo}({todo.name})")

        msg = self.get_memories(k=1)[0]  # find the most recent messages

        revison = await todo.run(
            syn_report=msg["syn_report"], revision_advice=msg["revision_advice"]
        )

        # logger.info(f'{selection}')
        msg = Message(content=revison, role=self.profile, cause_by=type(todo))

        return msg


class Analyst(Role):
    name: str = "__NAME__"
    profile: str = "P:__PROFILE__"

    def __init__(self, name, actions, watches, **kwargs):
        super().__init__(**kwargs)
        self.name = self.name.replace("__NAME__", name)
        self.profile = self.name.replace("__PROFILE__", name)
        self.addresses.add(self.name) 
        self.set_actions(actions)
        self._watch(watches)

    async def _observe(self) -> int:
        await super()._observe()
        # accept messages sent (from opponent) to self, disregard own messages from the last round
        self.rc.news = [msg for msg in self.rc.news if msg.send_to == {self.name}]
        return len(self.rc.news)

    def put_env_message(self, message):
        """Place the message into the Role object's private message buffer."""
        if not message:
            return
        self.rc.env.diag_buffer.push([message])

    async def _act(self) -> Message:
        # import pdb;pdb.set_trace()
        todo = self.rc.todo
        logger.info(f"{self._setting}: to do {todo}({todo.name})")

        announ = self.rc.env.announcement
        role_list = self.rc.env.role_list
        role_index = role_list.index(self.name)
        if role_index == len(role_list) - 1:
            next_name = role_list[0]
        else:
            next_name = role_list[role_index + 1]

        logger.info(announ)
        logger.info(f"________________{self.name}____________________________")

        msg = self.get_memories(k=1)[0]  # find the most recent messages
        # logger.info(msg)

        context = await todo.run(announ=announ, previous=msg, specialist_name=self.name)
        # logger.info(f"student : {context}")
        msg = Message(
            content=context,
            role=self.profile,
            cause_by=type(todo),
            sent_from=self.name,
            send_to=next_name,
        )
        self.put_env_message(msg)

        return msg


class Voter(Role):
    name: str = "__NAME__"
    profile: str = "P:__PROFILE__"

    def __init__(self, name, actions, watches, **kwargs):
        super().__init__(**kwargs)
        self.name = self.name.replace("__NAME__", name)
        self.profile = self.name.replace("__PROFILE__", name)
        self.addresses.add(self.name) 
        self.set_actions(actions + [Correct])
        self._watch(watches)

    async def _observe(self) -> int:
        await super()._observe()
        # import pdb;pdb.set_trace()
        # accept messages sent (from opponent) to self, disregard own messages from the last round
        self.rc.news = [msg for msg in self.rc.news if msg.send_to == {self.name}]
        return len(self.rc.news)

    def put_vote_opinion(self, message):
        """Place the message into the Role object's private message buffer."""
        if not message:
            return
        self.rc.env.vote_history[self.name] = message

    def put_revision_advice(self, message):
        """Place the message into the Role object's private message buffer."""
        if not message:
            return
        self.rc.env.revision_advice[self.name] = message

    async def _act(self) -> Message:

        todo = self.rc.todo
        logger.info(f"{self._setting}: to do {todo}({todo.name})")

        syn_report = self.rc.env.announcement
        role_list = self.rc.env.role_list
        role_index = role_list.index(self.name)
        if role_index == len(role_list) - 1:
            next_name = role_list[0]
        else:
            next_name = role_list[role_index + 1]

        # logger.info(msg)
        context = await todo.run(syn_report=syn_report, specialist_name=self.name)

        opinion = cleansing_voting(context)  # "yes" / "no"
        v_msg = f"Voting: {self.name}-{opinion}"
        logger.info(v_msg)
        self.put_vote_opinion(opinion)

        logger.info(f"Voter : {opinion}")
        if opinion == "no":
            next_do = self.actions[1]
            advice = await next_do.run(syn_report=syn_report, specialist_name=self.name)
            self.put_revision_advice(advice)

        msg = Message(
            content=context,
            role=self.profile,
            cause_by=type(todo),
            sent_from=self.name,
            send_to=next_name,
        )

        return msg
