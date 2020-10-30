import websocket, json, logging, traceback
from threading import Thread, Event
from urllib.parse import urlencode
from .channel import Channel, ChannelEvents
from .message import Message


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


class Client:
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
      on_message=lambda ws, message: self._on_message(message),
      on_error=lambda ws, message: self._on_error(message),
      on_close=lambda ws: self._on_close(),
      on_open=lambda ws: Thread(target=self._on_open, daemon=True).start())

    self.thread = None
    self.connect_event = Event()
    self.on_open_exc = None

  def _on_message(self, _message):
    message = Message.from_json(_message)
    logging.info("socket", message)

    if message.event == ChannelEvents.reply.value and message.ref in self.messages:
      self.messages[message.ref].respond(message.payload)
    else:
      channel = self.channels.get(message.topic)
      if channel:
        channel.receive(self, message)
      else:
        logging.info("socket", "unknown message", message)

    if message.ref in self.messages:
      del self.messages[message.ref]

    if self.on_message is not None:
      Thread(target=self.on_message, args=[message], daemon=True).start()

  def _on_error(self, message):
    if self.on_error is not None:
      self.on_error(self, message)
    self.connect_event.set()

  def _on_close(self):
    if self.on_close is not None:
      self.on_close(self)

  def _on_open(self):
    try:
      if self.on_open is not None:
        self.on_open(self)
    except Exception as e:
      self.on_open_exc = e
    finally:
      self.connect_event.set()

  def _run(self):
    try:
      self.websocket.run_forever(ping_interval=15)
    except:
      logging.error(traceback.format_exc())

  def push(self, topic, event, payload, cb=None, reply=False):
    if type(event) == ChannelEvents:
      event = event.value

    message = json.dumps({
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
    if topic not in self.channels:
      channel = Channel(self, topic, params)
      self.channels[topic] = channel

    return self.channels[topic]

  def after_connect(self):
    self.connect_event.wait()
    if self.on_open_exc:
      raise self.on_open_exc
