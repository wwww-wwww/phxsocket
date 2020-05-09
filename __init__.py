import websocket, json
from threading import Thread
from urllib.parse import urlencode
from .channel import Channel, ChannelEvents
from collections import namedtuple

Message = namedtuple(
  "Message", ["event", "topic", "payload", "ref"]
)

def decode(msg):
  msg = json.loads(msg)
  return Message(msg["event"], msg["topic"], msg["payload"], msg["ref"])

class SentMessage:
  def __init__(self, cb=None):
    self.cb = cb
    self.set = False
    self.message = None

  def respond(self, message):
    self.set = True
    self.message = message
    if self.cb is not None:
      self.cb(message)

  def wait_for_response(self):
    while not self.set:
      pass

    return self.message

class Socket:
  def __init__(self, url, params):
    qs_params = {"vsn": "1.0.0", **params}
    self.url = url + "?" + urlencode(qs_params)
    self.params = params

    self.channels = {}
    self.messages = {}
    self._ref = 0

    self.on_open = None
    self.on_message = None
    self.on_error = None
    self.on_close = None
    self.websocket = websocket.WebSocketApp(
      self.url,
      on_message=lambda ws, message: self._on_message(ws, message),
      on_error=lambda ws, error: self._on_error(ws, error),
      on_close=lambda ws: self._on_close(ws),
      on_open=lambda ws: self._on_open(ws)
    )

    self.thread = None
  
  def _on_message(self, ws, _message):
    message = decode(_message)

    if message.event == ChannelEvents.reply.value and message.ref in self.messages:
      self.messages[message.ref].respond(message.payload)
      del self.messages[message.ref]
    else:
      channel = self.channels.get(message.topic)
      if channel:
        channel.receive(self, message)
      else:
        print("socket", "unknown message", message)

    if self.on_message is not None:
      self.on_message(self, message)
  
  def _on_error(self, ws, message):
    if self.on_error is not None:
      self.on_error(self, message)
  
  def _on_close(self, ws):
    if self.on_close is not None:
      self.on_close(self)

  def _on_open(self, ws):
    if self.on_open is not None:
      Thread(target=lambda: self.on_open(self), daemon=True).start()

  def _run(self):
    self.websocket.run_forever(ping_interval=15)

  def send_message(self, topic, event, payload, cb=None):
    message = json.dumps(
    {
      "event": event,
      "topic": topic,
      "ref": self._ref,
      "payload": payload
    })

    sent_message = SentMessage(cb)

    self.messages[self._ref] = sent_message

    self.websocket.send(message)

    self._ref = self._ref + 1

    return sent_message

  def close(self):
    self.websocket.close()

  def connect(self):
    self.thread = Thread(target=self._run, daemon=True)
    self.thread.start()

  def channel(self, topic, params):
    channel = Channel(self, topic, params)
    self.channels[topic] = channel
    return channel
