# Setup Guide for Monopoly LAN Game

## System Requirements

- Python 3.8 or higher
- Network connectivity between PCs (LAN)
- Windows, macOS, or Linux

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/monopoly-lan-game.git
cd monopoly-lan-game
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Find Your Server PC's IP Address

**On Windows:**
```cmd
ipconfig
```
Look for IPv4 Address under your LAN adapter (typically starts with 192.168 or 10.x.x.x)

**On macOS/Linux:**
```bash
ifconfig
```
Look for the inet address on your network interface

## Running the Game

### Step 1: Start the Server

On the PC that will host the game:

```bash
python server/game_server.py
```

The server will display its IP address and wait for players to connect.

### Step 2: Connect Clients

On each player's PC:

```bash
python client/game_client.py
```

When prompted:
- Enter your player name
- Enter the server IP address (from Step 1)

Repeat this for each player (2-6 players)

### Step 3: Start the Game

Once all players have connected to the server, press Enter or send a "start" command from the server to begin playing.

## Network Troubleshooting

### Players can't connect to server

1. **Check firewall**: Make sure port 5555 is not blocked by your firewall
2. **Verify IP address**: Ensure all clients are using the correct server IP
3. **Check network**: All PCs must be on the same network
4. **Disable VPN**: Virtual networks may interfere with local connections

### Connection drops during gameplay

1. Check network stability
2. Ensure no firewall is interfering with UDP traffic
3. Check for network congestion

## Port Configuration

The default port is 5555. To use a different port, modify the server and client code:

**Server (server/game_server.py):**
```python
server = GameServer(port=YOUR_PORT)
```

**Client (client/game_client.py):**
```python
client.connect_to_server(server_ip, server_port=YOUR_PORT)
```
