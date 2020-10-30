# phxsocket
### Synchronous phoenix websocket client using callbacks
[Phoenix channels](https://hexdocs.pm/phoenix/channels.html)
## Requirements
`websocket_client`

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
def on_open(socket):
  channel = socket.channel("room:roomname", {"more options": "something else"})
  
  join_success, resp = self.channel.join()

def reconnect():
  socket.connect()

socket.on_open = on_open
socket.on_error = lambda socket, message: (print(message), reconnect())
socket.connect()
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
