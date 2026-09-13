# Monopoly LAN Game

A multiplayer Monopoly board game that can be played over LAN-connected PCs.

## Features

- **Multiplayer Support**: Play with up to 6 players on the same LAN network
- **Real-time Gameplay**: Turn-based system with live updates
- **Cross-Platform**: Windows, macOS, and Linux support
- **Network Communication**: UDP socket-based networking for fast communication
- **Game Features**:
  - Buy and sell properties
  - Pay rent to other players
  - Chance and Community Chest cards
  - Jail mechanics
  - Auction system for properties
  - Bank management

## Project Structure

```
monopoly-lan-game/
├── server/              # Game server (runs on one PC)
├── client/              # Game client (runs on all player PCs)
├── core/                # Shared game logic
├── assets/              # Game assets (board, tokens, etc.)
└── docs/                # Documentation
```

## Quick Start

### Prerequisites
- Python 3.8+
- Pygame
- Network connection between PCs (LAN)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/monopoly-lan-game.git
cd monopoly-lan-game

# Install dependencies
pip install -r requirements.txt
```

### Running the Game

**On the Server PC:**
```bash
python server/game_server.py
```

**On Each Player PC:**
```bash
python client/game_client.py
```

Then connect to the server by entering its IP address when prompted.

## How to Play

1. Start the server on one PC
2. Launch the client on each player's PC
3. Connect all clients to the server's IP address
4. Wait for all players to connect
5. Roll the dice and move around the board
6. Buy properties, collect rent, and become the wealthiest player!

## Game Rules

- Players start with $1,500
- Roll two dice each turn
- Move that many spaces
- Buy unowned properties or pay rent
- Complete property sets to build houses/hotels
- Last player with money wins

## Contributing

Feel free to submit issues and pull requests to improve the game!

## License

MIT License - See LICENSE file for details
