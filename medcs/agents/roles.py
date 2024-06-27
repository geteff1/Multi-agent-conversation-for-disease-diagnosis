import asyncio

from metagpt.roles import Role
from metagpt.logs import logger
from metagpt.schema import Message
from metagpt.actions import UserRequirement
from metagpt.utils.common import any_to_str



class Attending_Physician(Role):
    name: str = "Attending Physician"
    profile: str = "Attending Physician"
    num_specialists: int = 5
    
    def __init__(self, actions, **kwargs):
        super().__init__(**kwargs)
        self.set_actions(actions)
        self._watch([UserRequirement])
        

    # async def _think(self):
    #     news = self.rc.news[0]
    #     import pdb;pdb.set_trace()
    #     if news.sent_from == "Human":
    #         # 消息接收范围为全体角色的，做公开发言（发表投票观点也算发言）
    #         self.rc.todo = 
    #     elif self.profile in news.restricted_to:
    #         # FIXME: hard code to split, restricted为"Moderator"或"Moderator, 角色profile"
    #         # Moderator加密发给自己的，意味着要执行角色的特殊动作
    #         self.rc.todo = self.special_actions[0]()
    #     return True
        
    async def _act(self) -> Message:
        todo = self.rc.todo
        logger.info(f"{self._setting}: ready to {self.rc.todo}")
        
        
        msg = self.get_memories()  # 获取所有记忆
        # logger.info(msg)
        selection = await todo.run(msg=msg, num_specialists=self.num_specialists)
        # logger.info(f'{selection}')
        msg = Message(content=selection, role=self.profile,
                      cause_by=type(todo))
        
        return msg
    
    
class Specialist(Role):
    name: str = "Specialist {index}"
    profile: str = "Specialist {name}"
    
    def __init__(self, name, index, actions, watches, **kwargs):
        super().__init__(**kwargs)
        self.name = self.name.format(index=index)
        self.profile = self.profile.format(name=name)
        self.set_actions(actions)
        self._watch(watches)

    async def _observe(self) -> int:
        await super()._observe()
        # accept messages sent (from opponent) to self, disregard own messages from the last round
        import pdb;pdb.set_trace()
        self.rc.news = [msg for msg in self.rc.news if msg.send_to == {self.name}]
        return len(self.rc.news)

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        import pdb;pdb.set_trace()
        msg = self.get_memories()  # 获取所有记忆
        # logger.info(msg)
        context = await todo.run().run(msg)
        logger.info(f'student : {context}')
        msg = Message(
            content=context, 
            role=self.profile,
            cause_by=type(todo),
            sent_from=self.name,)

        return msg