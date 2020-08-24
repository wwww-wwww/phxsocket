import websocket, json
from threading import Thread, Event
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
    self.connect_event = Event()

  def _on_message(self, ws, _message):
    message = decode(_message)

    if message.event == ChannelEvents.reply.value and message.ref in self.messages:
      self.messages[message.ref].respond(message.payload)
    else:
      channel = self.channels.get(message.topic)
      if channel:
        channel.receive(self, message)
      else:
        print("socket", "unknown message", message)

    if message.ref in self.messages:
      del self.messages[message.ref]

    if self.on_message is not None:
      Thread(target=lambda: self.on_message(self, message), daemon=True).start()

  def _on_error(self, ws, message):
    if self.on_error is not None:
      self.on_error(self, message)
    self.connect_event.set()

  def _on_close(self, ws):
    if self.on_close is not None:
      self.on_close(self)

  def _on_open(self, ws):
    if self.on_open is not None:
      Thread(target=lambda: (self.on_open(self), self.connect_event.set()), daemon=True).start()

  def _run(self):
    self.websocket.run_forever(ping_interval=15)

  def send_message(self, topic, event, payload, cb=None, reply=False):
    message = json.dumps(
    {
      "event": event,
      "topic": topic,
      "ref": self._ref,
      "payload": payload
    })

    sent_message = SentMessage(cb)

    if reply or cb:
      self.messages[self._ref] = sent_message

    self.websocket.send(message)

    self._ref = self._ref + 1
    
    if reply or cb:
      return sent_message

  def close(self):
    self.websocket.close()

  def connect(self):
    self.thread = Thread(target=self._run, daemon=True)
    self.thread.start()

  def channel(self, topic, params={}):
    channel = Channel(self, topic, params)
    self.channels[topic] = channel
    return channel

  def after_connect(self):
    self.connect_event.wait()
