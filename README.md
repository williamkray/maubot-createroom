# create room bot

# this plugin is now deprecated, and its functionality (and improvements!) have been moved into
[communitybot](https://github.com/williamkray/maubot-communitybot)

very stupid bot that:

1. creates a room
2. assigns the room an alias that matches the name (sanitized)
3. make the room part of a space (as defined in the config)
4. grant admin roles to a list of users
5. invites a list of users to the room

in order for all this to work, **the bot must have enough power in the space to send state events**. if this is not the
case, the bot will create the room but will throw errors when trying to send state events to the space, and everything
after that will bomb out.
