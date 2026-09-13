# Quick Start Guide - Monopoly LAN Game (New Version)

## What's New?

- **Room/Lobby System**: Create a room and share the code with others
- **Pygame GUI**: Beautiful graphical interface
- **WebSocket Server**: Better real-time communication
- **Easy Connection**: No need to enter IP addresses!

## Installation

```bash
# Clone or navigate to repository
cd monopoly-lan-game

# Install dependencies
pip install -r requirements.txt
```

## Running the Game

### Step 1: Start the Server

**On any PC (the server PC):**

```bash
python server/websocket_server.py
```

You should see:
```
============================================================
Monopoly LAN Game - WebSocket Server
============================================================
Server running on http://localhost:5555
WebSocket connection: ws://localhost:5555
============================================================
```

### Step 2: Start the GUI Clients

**On the host's PC:**

```bash
python client/gui_client.py
```

**On each other player's PC:**

```bash
python client/gui_client.py
```

## How to Play

### 1. Main Menu
- Enter your player name
- Click **"Create Room"** to start a new game (you become the host)
- Or click **"Join Room"** to join an existing game

### 2. Room Screen
- You'll get a **room code** (e.g., `A7K2X`)
- Share this code with your friends
- Other players enter this code to join
- All players in the room will see each other

### 3. Lobby
- Wait for all players to join
- Click **"I'm Ready!"** when ready to play
- Once all players are ready, the **host** clicks **"Start Game"**

### 4. Game
- Roll dice to move around the board
- Buy properties when you land on them
- Pay rent when you land on opponents' properties
- Become the last player with money to win!

## Connection Setup

### Single Machine (Testing)

Everything runs on localhost automatically.

```bash
# Terminal 1
python server/websocket_server.py

# Terminal 2
python client/gui_client.py

# Terminal 3
python client/gui_client.py

# ...repeat for more players
```

### Multiple Machines (LAN)

**On Server PC:**
1. Run: `python server/websocket_server.py`
2. Note the server IP address (e.g., `192.168.1.100`)

**On Each Player PC:**
1. Edit `client/gui_client.py` line: `MonopolyGUIClient(server_url="http://192.168.1.100:5555")`
2. Replace `192.168.1.100` with your server IP
3. Run: `python client/gui_client.py`

### Find Your Server IP

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" (usually `192.168.x.x`)

**macOS/Linux:**
```bash
ifconfig
```
Look for "inet" address

## Troubleshooting

### Players can't connect to server

1. **Check firewall**: Allow port 5555 through your firewall
2. **Check server IP**: Make sure all clients use the correct server IP
3. **Same network**: All PCs must be on the same LAN

### "Room not found" error

- Make sure the room code is typed correctly (case-sensitive)
- Server might have crashed - restart it

### Connection drops

- Check network stability
- Firewall might be blocking UDP traffic
- Try restarting both server and clients

## Game Controls

| Action | Button |
|--------|--------|
| Enter Name | Type in text box |
| Create Room | Click "Create Room" button |
| Join Room | Click "Join Room" button |
| Set Ready | Click "I'm Ready!" button |
| Start Game | Click "Start Game" button (host only) |
| Roll Dice | Click dice or press SPACE |
| Buy Property | Click property or press B |
| End Turn | Click "End Turn" or press E |

## Next Steps

Try these:

1. **Create a room** and test joining with another client on the same PC
2. **Share room code** with a friend and join across PCs
3. **Play a full game** and see who wins!

## Getting Help

Check the documentation:
- `docs/SETUP.md` - Detailed setup instructions
- `docs/GAMEPLAY.md` - Full game rules
- `docs/TESTING.md` - How to test the game
