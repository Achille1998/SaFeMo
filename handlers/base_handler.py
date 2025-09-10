#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inspect
import json
from abc import ABC
from asyncio import AbstractEventLoop
from functools import partial
from typing import Any, Callable, List, Optional, Tuple, Type, Union
from tornado.escape import json_decode, json_encode
from tornado.web import RequestHandler
import logging
logger = logging.getLogger(inspect.currentframe().f_back.f_globals["__name__"])


class BaseHandler(RequestHandler, ABC):

    def write(self, chunk: Union[str, bytes, dict]) -> None:
        if isinstance(chunk, dict):
            chunk = json.dumps(chunk)
        super().write(chunk)
        self.finish()

    def success(self, msg):
        logger.debug(msg)
        self.write({"status": "ok", "msg": msg})
        self.finish()

    def error(self, msg):
        logger.error(msg)
        self.write({"status": "ko", "msg": msg})
        self.finish()

    def get_body_attribute(self, name: str, default: Optional[Any] = None) -> Optional[Any]:
        body_obj = json_decode(self.request.body)
        return body_obj.get(name, default)

    def get_body_attributes(self) -> Optional[Any]:
        body_obj = json_decode(self.request.body)
        return body_obj

    async def async_query(self, dao: Callable, *args, **kwargs):
        self.require_setting("loop", "Async query requires a loop to be defined in settings")
        loop: AbstractEventLoop = self.settings.get("loop")
        return await loop.run_in_executor(None, partial(dao, *args, **kwargs))

