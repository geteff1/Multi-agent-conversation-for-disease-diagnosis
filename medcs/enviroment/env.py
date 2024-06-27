from typing import Iterable

from pydantic import Field

from metagpt.environment.base_env import Environment
from metagpt.schema import Message


from typing import Type, Dict, Iterable, Set


from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny, model_validator

from metagpt.schema import Message, MessageQueue
from metagpt.context import Context


class MedCSEnv(Environment):

    announcement: str = Field(default="")
    diag_buffer: MessageQueue = Field(default_factory=MessageQueue, exclude=True)
    vote_history: dict = {}  # For debug
    revision_advice: dict = {}

    role_list: list = []

    def add_announ(self, announ):
        self.announcement = announ

    def add_role_list(self, role_list):
        self.role_list = role_list

