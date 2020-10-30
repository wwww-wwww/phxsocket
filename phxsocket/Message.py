import json, typing


class Message(typing.NamedTuple):
  event: str
  topic: str
  payload: str
  ref: int

  @classmethod
  def from_json(cls, msg):
    msg = json.loads(msg)
    return cls(msg["event"], msg["topic"], msg["payload"], msg["ref"])
