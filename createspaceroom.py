from typing import Awaitable, Type, Optional, Tuple
import json
import time
import re

from mautrix.client import Client
from mautrix.types import (Event, StateEvent, EventID, UserID, FileInfo, EventType,
                            RoomID, RoomAlias, ReactionEvent, RedactionEvent)
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot import Plugin, MessageEvent
from maubot.handlers import command, event


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("admins")
        helper.copy("mods")
        helper.copy("space_id")
        helper.copy("invitees")
        helper.copy("server")


class CreateSpaceRoom(Plugin):

    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()
        

    @command.new("createroom", help="give me a room name and i'll create it and add it to the space")
    @command.argument("roomname", pass_raw=True, required=True)
    async def create_that_room(self, evt: MessageEvent, roomname: str) -> None:
        if (roomname == "help") or len(roomname) == 0:
            await evt.reply('pass me a room name (like "cool topic") and i will create it and add it to the space')
        else:
            if evt.sender in self.config["admins"] or evt.sender in self.config["mods"]:
                try:
                    sanitized_name = re.sub(r"[^a-zA-Z0-9]", '', roomname).lower()
                    invitees = self.config['invitees']
                    space_id = self.config['space_id']
                    #server = self.client.whoami().domain
                    server = self.config['server']
                    pl_override = {"users": {self.client.mxid: 100}}
                    for u in self.config['admins']:
                        pl_override["users"][u] = 100
                    pl_json = json.dumps(pl_override)

                    mymsg = await evt.respond(f"creating {sanitized_name}, give me a minute...")
                    #self.log.info(mymsg)
                    room_id = await self.client.create_room(alias_localpart=sanitized_name, name=roomname,
                            invitees=invitees, power_level_override=pl_override)
                    await evt.respond(f"room created, alias is #{sanitized_name}:{server}", edits=mymsg)

                    parent_event_content = json.dumps({'auto_join': False, 'suggested': False, 'via': [server]})
                    child_event_content = json.dumps({'canonical': True, 'via': [server]})
                    join_rules_content = json.dumps({'join_rule': 'restricted', 'allow': [{'type': 'm.room_membership',
                        'room_id': space_id}]})

                    await self.client.send_state_event(space_id, 'm.space.child', parent_event_content, state_key=room_id)
                    await self.client.send_state_event(room_id, 'm.space.parent', child_event_content, state_key=space_id)
                    await self.client.send_state_event(room_id, 'm.room.join_rules', join_rules_content, state_key="")

                    await evt.respond(f"room states updated", edits=mymsg)

                except Exception as e:
                    await evt.respond(f"i tried, but something went wrong: \"{e}\"", edits=mymsg)
            else:
                await evt.reply("you're not the boss of me!")

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config
