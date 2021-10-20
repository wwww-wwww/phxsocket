import json, typing
from threading import Event


class Message(typing.NamedTuple):
  event: str
  topic: str
  payload: str
  ref: int

  @classmethod
  def from_json(cls, msg):
    msg = json.loads(msg)
    return cls(msg["event"], msg["topic"], msg["payload"], msg["ref"])


class SentMessage:
  def __init__(self, cb=None):
    self.cb = cb
    self.event = Event()
    self.message = None

  def respond(self, message):
    self.message = message
    if self.cb:
      self.cb(message)
    self.event.set()

  def wait_for_response(self):
    self.event.wait()
    return self.message
