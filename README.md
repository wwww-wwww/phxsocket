# phxsocket
### Synchronous phoenix websocket client using callbacks
[Phoenix channels](https://hexdocs.pm/phoenix/channels.html)
## Requirements
`websockets`

## Usage
Import the package
```python
import phxsocket
```

Create socket client
```python
socket = phxsocket.Client("wss://target.url/websocket", {"options": "something"})
```

Connect and join a channel
```python
if socket.connect(): # blocking, raises exception on failure
  channel = socket.channel("room:roomname", {"more options": "something else"})
  join_success, resp = channel.join()
```

Alternatively
```python
def connect_to_channel(socket):
  channel = socket.channel("room:roomname", {"more options": "something else"})
  join_success, resp = channel.join()
  
socket.on_open = connect_to_channel
connection = socket.connect(blocking=False)

connection.wait() # blocking, raises exception on failure
```

Reconnect on disconnection
```python
socket.on_close = lambda socket: socket.connect()
```

Subscribe to events
```python
def do_something(payload):
  thing = payload["thing"]

channel.on("eventname", do_something)
```

Push data to a channel
```python
channel.push("eventname", {"some": "data"})
```

Push data and wait for a response
```python
message = channel.push("eventname", {"some": "data"}, reply=True)
response = message.wait_for_response() # blocking
```

Push data and react to the response with a callback
```python
def respond(payload):
  print(payload)

channel.push("eventname", {"some": "data"}, respond)
```

Leave a channel
```python
channel.leave()
```

Disconnect
```python
socket.close()
```
