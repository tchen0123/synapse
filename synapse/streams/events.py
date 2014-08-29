# -*- coding: utf-8 -*-
# Copyright 2014 matrix.org
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from twisted.internet import defer

from synapse.types import StreamToken

from synapse.handlers.presence import PresenceEventSource
from synapse.handlers.room import RoomEventSource


class NullSource(object):
    """This event source never yields any events and its token remains at
    zero. It may be useful for unit-testing."""
    def __init__(self, hs):
        pass

    def get_new_events_for_user(self, user, from_token, limit):
        return defer.succeed(([], from_token))

    def get_current_token_part(self):
        return defer.succeed(0)

    def get_pagination_rows(self, user, pagination_config, key):
        return defer.succeed(([], pagination_config.from_token))


class EventSources(object):
    SOURCE_TYPES = {
        "room": RoomEventSource,
        "presence": PresenceEventSource,
    }

    def __init__(self, hs):
        self.sources = {
            name: cls(hs)
            for name, cls in EventSources.SOURCE_TYPES.items()
        }

    @staticmethod
    def create_token(events_key, presence_key):
        return StreamToken(events_key=events_key, presence_key=presence_key)

    @defer.inlineCallbacks
    def get_current_token(self):
        events_key = yield self.sources["room"].get_current_token_part()
        presence_key = yield self.sources["presence"].get_current_token_part()
        token = EventSources.create_token(events_key, presence_key)
        defer.returnValue(token)


class StreamSource(object):
    def get_new_events_for_user(self, user, from_token, limit):
        raise NotImplementedError("get_new_events_for_user")

    def get_current_token_part(self):
        raise NotImplementedError("get_current_token_part")

    def get_pagination_rows(self, user, pagination_config, key):
        raise NotImplementedError("get_rows")