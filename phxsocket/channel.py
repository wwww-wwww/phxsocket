from enum import Enum
from typing import Union, Callable, Tuple
from .message import SentMessage
import traceback


class ChannelConnectError(Exception):
  pass


class ChannelEvents(Enum):
  close = "phx_close"
  error = "phx_error"
  join = "phx_join"
  reply = "phx_reply"
  leave = "phx_leave"


class Channel:
  def __init__(self, socket, topic, params):
    self.socket = socket
    self.topic = topic
    self.params = params
    self.on_message = None
    self.on_close = None
    self.events = {}

  def join(self) -> Union[dict, list, str, int, float, bool]:
    join = self.socket.push(self.topic,
                            ChannelEvents.join,
                            self.params,
                            reply=True)

    response = join.wait_for_response()
    if response["status"] != "ok":
      raise ChannelConnectError(response["response"])

    return response["response"]

  def leave(self) -> Tuple[bool, Union[dict, list, str, int, float, bool]]:
    leave = self.socket.push(self.topic,
                             ChannelEvents.leave,
                             self.params,
                             reply=True)
    try:
      return True, leave.response()
    except:
      return False, traceback.format_exc()

  def push(self,
           event: Union[ChannelEvents, str],
           payload: Union[dict, list, str, int, float, bool],
           cb: Callable = None,
           reply: bool = False) -> Union[SentMessage, None]:
    msg = self.socket.push(self.topic, event, payload, cb, reply)
    return msg

  def on(
      self, event: Union[ChannelEvents, str],
      cb: Callable[[Union[dict, list, str, int, float, bool]], None]) -> None:
    self.events[event] = cb

  def receive(self, socket, message):
    if message.event == ChannelEvents.close.value:
      if self.on_close:
        self.on_close()
    else:
      if message.event in self.events:
        self.events[message.event](message.payload)
      if self.on_message:
        self.on_message(socket, message.event, message.payload)
