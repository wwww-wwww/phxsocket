# phxsocket

### Synchronous phoenix websocket client using callbacks

[Phoenix channels](https://hexdocs.pm/phoenix/channels.html)

## Requirements

`websockets`

## Usage

### Import the package

```python
import phxsocket
```

### Create socket client

```elixir
# endpoint.ex
socket "/socket", MyAppWeb.Socket, websocket: true, longpoll: false
```

```python
socket = phxsocket.Client("wss://target.url/socket/websocket", {"name": "my name"})
```

Socket params go to Phoenix.Socket connect/3

### Connect and join a channel

```elixir
# mysocket.ex
defmodule MyAppWeb.Socket do
  use Phoenix.Socket

  channel("channel:*", MyAppWeb.Channel)

  def connect(%{"name" => name} = params, socket, _connect_info) do
    {:ok, socket |> assign(name: name)}
  end

  def id(socket), do: nil
end

defmodule MyAppWeb.Channel do
  use Phoenix.Channel

  def join("channel:" <> room_name, %{"password" => password}, socket) do
    if password == "1234" do
      {:ok, socket}
    else
      {:error, %{reason: "unauthorized"}}
    end
  end
end
```

```python
if socket.connect(): # blocking, raises exception on failure
  channel = socket.channel("channel:my room", {"password": "1234"})
  resp = channel.join() # also blocking, raises exception on failure
```

Alternatively

```python
def connect_to_channel(socket):
  channel = socket.channel("channel:my room", {"password": "1234"})
  resp = channel.join()

socket.on_open = connect_to_channel
connection = socket.connect(blocking=False)

connection.wait() # blocking, raises exception on failure
```

### Reconnect on disconnection

```python
socket.on_close = lambda socket: socket.connect()
```

### Subscribe to events

```python
def do_something(payload):
  content = payload["content"]

channel.on("message", do_something)
```

```elixir
MyAppWeb.Endpoint.broadcast("channel:my room", "message", %{"content": "hello"})
```

### Push data to a channel

```elixir
defmodule MyAppWeb.Channel do
...
def handle_in("message", %{"content" => content}, socket) do
  IO.inspect("received from #{socket.assigns.name}: #{content}")
  {:reply, {:ok, "hello"}, socket}
end
```

```python
channel.push("message", {"content": "hello"})
```

This throws away the reply if the return value of handle_in is :reply

### Push data and wait for a response

```python
message = channel.push("message", {"content": "hello"}, reply=True)
payload = message.wait_for_response() # blocking
```

### Push data and react to the response with a callback

```python
def response(payload):
  print(payload["status"]) # ok
  print(payload["response"]) # hello

channel.push("message", {"content": "hello"}, response)
```

### Leave a channel

```python
channel.leave()
```

### Disconnect

```python
socket.close()
```
