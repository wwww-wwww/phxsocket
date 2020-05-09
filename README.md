# phxsocket
### synchronous websocket client using callbacks
[Phoenix channels](https://hexdocs.pm/phoenix/channels.html)
## requirements
`websocket_client`

## usage
import the package
```python
from phxsocket import Socket
```

create a socket
```python
socket = Socket("wss://target.url/websocket", {"options": "something"})
```

connect and join a channel
```python
def on_open(socket):
  channel = socket.channel("room:roomname", {"more options": "something else"})
  
  join_success, resp = self.channel.join()

socket.on_open = on_open
socket.on_error = lambda socket, message: (print(message), self.reconnect())
socket.connect()
```

subscribe to events
```python
def do_something(payload):
  thing = payload["thing"]

channel.on("eventname", do_something)
```

push data to a channel
```python
channel.push("eventname", {"some": "data"})
```

push data and wait for a response
```python
message = channel.push("eventname", {"some": "data"})
response = message.wait_for_response() # blocking
```

push data and react to the response with a callback
```python
channel.push("eventname", {"some": "data"}, lambda payload: print(payload))
```

leave a channel
```python
channel.leave()
```

disconnect
```python
socket.close()
```