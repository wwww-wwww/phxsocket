from enum import Enum

class ChannelEvents(Enum):
  close = "phx_close"
  error = "phx_error"
  join = "phx_join"
  reply = "phx_reply"
  leave = "phx_leave"

class ChannelConnectException(Exception):
  pass

class Channel:
  def __init__(self, socket, topic, params):
    self.socket = socket
    self.topic = topic
    self.params = params
    self.on_message = None
    self.on_close = None
    self.events = {}

  def join(self):
    join = self.socket.send_message(
      self.topic, ChannelEvents.join.value, self.params, reply=True
    )
    
    try:
      response = join.wait_for_response()
      if response["status"] == "ok":
        return response["response"]
      else:
        raise ChannelConnectException(response["response"])
    except:
      raise ChannelConnectException(response["response"])

  def leave(self):
    leave = self.socket.send_message(
      self.topic, ChannelEvents.leave.value, self.params, reply=True
    )
    try:
      return True, leave.response()
    except Exception as e:
      return False, "Failed to leave?"

  def push(self, event, payload, cb=None, reply=False):
    msg = self.socket.send_message(self.topic, event, payload, cb, reply)
    return msg

  def on(self, event, cb):
    self.events[event] = cb

  def receive(self, socket, message):
    if message.event in ChannelEvents.close.value:
      if self.on_close is not None:
        self.on_close()
    else:
      if message.event in self.events:
        self.events[message.event](message.payload)
      if self.on_message is not None:
        self.on_message(socket, message.event, message.payload)
