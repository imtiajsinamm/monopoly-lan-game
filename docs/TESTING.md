# Testing Guide for Monopoly LAN Game

## 1. Local Testing (Single Machine)

### Test Case 1: Basic Server Startup
```bash
# Terminal 1 - Start the server
python server/game_server.py
```
**Expected Output:**
```
==================================================
Monopoly LAN Game Server
==================================================
Server started on 0.0.0.0:5555
Waiting for players to connect...
==================================================
```

### Test Case 2: Client Connection
```bash
# Terminal 2 - Start first client
python client/game_client.py

# When prompted:
# Enter your player name: Alice
# Enter server IP address (default: 127.0.0.1): 127.0.0.1
```

**Expected Output:**
```
Successfully connected to server at 127.0.0.1:5555
Join acknowledged!
Connected players: ['Alice']
```

### Test Case 3: Multiple Players
```bash
# Terminal 3 - Start second client
python client/game_client.py

# When prompted:
# Enter your player name: Bob
# Enter server IP address (default: 127.0.0.1): 127.0.0.1
```

**Expected Output on Server:**
```
Player 'Alice' joined from ('127.0.0.1', 54321)
Players connected: 1
Player 'Bob' joined from ('127.0.0.1', 54322)
Players connected: 2
```

### Test Case 4: Start Game
Once you have 2+ players connected, send a start command. You should see:
- Game initialization
- Board creation
- Player state display

---

## 2. LAN Testing (Multiple Machines)

### Prerequisites
- Server PC: Let's say **192.168.1.100**
- Player PC 1: Any other machine on the same network
- Player PC 2: Another machine on the same network
- All machines on the same Wi-Fi/LAN

### Setup Steps

**Step 1: Start Server**
```bash
# On Server PC
python server/game_server.py

# Note the IP address displayed (192.168.1.100)
```

**Step 2: Connect from Other PCs**
```bash
# On Player PC 1
python client/game_client.py
# Enter player name: Player1
# Enter server IP: 192.168.1.100

# On Player PC 2
python client/game_client.py
# Enter player name: Player2
# Enter server IP: 192.168.1.100
```

---

## 3. Unit Testing

### Test Core Game Logic

Create a test file: `test_game_logic.py`

```python
import sys
sys.path.insert(0, '.')

from core.game import Game
from core.player import Player
from core.board import Board
from core.property import Property

def test_player_creation():
    """Test creating a player"""
    player = Player("Alice", 1500)
    assert player.name == "Alice"
    assert player.money == 1500
    assert player.position == 0
    print("✓ Player creation test passed")

def test_player_movement():
    """Test player movement"""
    player = Player("Bob", 1500)
    player.move(10, 40)
    assert player.position == 10
    print("✓ Player movement test passed")

def test_player_pass_go():
    """Test passing GO"""
    player = Player("Charlie", 1500)
    initial_money = player.money
    player.move(35, 40)  # Move to position 35
    player.move(10, 40)  # Move to position 5 (45 % 40), crossing GO
    assert player.position == 5
    assert player.money > initial_money  # Should collect $200
    print("✓ Pass GO test passed")

def test_game_creation():
    """Test creating a game"""
    game = Game(["Alice", "Bob", "Charlie"])
    assert len(game.players) == 3
    assert game.current_player_index == 0
    assert not game.game_over
    print("✓ Game creation test passed")

def test_board_creation():
    """Test board creation"""
    board = Board()
    assert len(board.properties) == 40
    assert board.properties[0].name == "GO"
    assert board.properties[39].name == "Boardwalk"
    print("✓ Board creation test passed")

def test_property_rent():
    """Test property rent calculation"""
    prop = Property(1, "Mediterranean Avenue", 60, "brown", "street")
    prop.owner = "Alice"
    
    # No improvements: base rent = price / 10
    base_rent = prop.calculate_rent()
    assert base_rent == 6  # 60 / 10
    
    # With 1 house
    prop.add_house()
    rent_with_house = prop.calculate_rent()
    assert rent_with_house == 60  # base_rent * 1 (multiplier)
    print("✓ Property rent test passed")

def test_dice_roll():
    """Test dice rolling"""
    from core.dice import Dice
    dice = Dice()
    die1, die2 = dice.roll()
    assert 1 <= die1 <= 6
    assert 1 <= die2 <= 6
    print("✓ Dice roll test passed")

if __name__ == "__main__":
    test_player_creation()
    test_player_movement()
    test_player_pass_go()
    test_game_creation()
    test_board_creation()
    test_property_rent()
    test_dice_roll()
    print("\n✓ All tests passed!")
```

**Run the tests:**
```bash
python test_game_logic.py
```

---

## 4. Manual Gameplay Testing

### Test Scenario 1: Basic Gameplay
1. Start server
2. Connect 2 players
3. Player 1: Roll dice (should see result)
4. Player 1: Move to a property
5. Player 1: Buy the property
6. Player 2: Roll dice and move
7. Verify game state updates on all clients

### Test Scenario 2: Rent Payment
1. Player 1 buys a property
2. Player 2 lands on Player 1's property
3. Player 2's money should decrease (rent paid)
4. Player 1's money should increase (rent received)

### Test Scenario 3: Multiple Players
1. Start server
2. Connect 3-4 players
3. Verify all players see correct game state
4. Check that turns rotate correctly
5. Verify all players receive updates

### Test Scenario 4: Player Bankruptcy
1. Have a player repeatedly pay rent
2. Eventually player's money reaches $0
3. Player should be marked as bankrupt
4. Game should handle their removal

---

## 5. Automated Testing Script

Create `run_tests.py` to run all tests at once:

```python
#!/usr/bin/env python3
"""Automated test runner for Monopoly LAN Game"""

import subprocess
import sys
import time

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"{'='*50}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(result.stdout)
        if result.returncode != 0:
            print(f"ERROR: {result.stderr}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print("Test timed out")
        return False
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def main():
    tests_passed = 0
    tests_failed = 0
    
    # Test game logic
    if run_command("python test_game_logic.py", "Unit Tests - Game Logic"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {tests_passed} passed, {tests_failed} failed")
    print(f"{'='*50}")
    
    return 0 if tests_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

**Run all tests:**
```bash
python run_tests.py
```

---

## 6. Network Troubleshooting Tests

### Test Network Connectivity
```bash
# Check if server PC is reachable
ping 192.168.1.100

# Check if port 5555 is open
# On server PC, use a port scanner or:
netstat -an | grep 5555  # Linux/macOS
netstat -ano | findstr 5555  # Windows
```

### Test Firewall Settings
```bash
# Linux/macOS: Allow port 5555
sudo ufw allow 5555

# Windows: Add exception to Windows Defender Firewall
# Settings > Privacy & Security > Firewall > Allow an app through firewall
```

---

## 7. Performance Testing

### Measure Network Latency
```python
import time
import socket
import json

def measure_latency(server_ip, server_port):
    """Measure round-trip time to server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 0))
    
    message = json.dumps({'type': 'ping'}).encode('utf-8')
    start = time.time()
    sock.sendto(message, (server_ip, server_port))
    end = time.time()
    
    latency_ms = (end - start) * 1000
    print(f"Latency: {latency_ms:.2f}ms")
    sock.close()

# Run it
measure_latency("192.168.1.100", 5555)
```

---

## 8. Debugging Tips

### Enable Debug Output
Add this to `server/game_server.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Your debug message")
```

### Check Server Logs
The server prints all connections and actions. Monitor these for errors.

### Check Client Logs
The client prints game state updates and errors. Use these to debug gameplay issues.

### Use Network Monitor
Monitor network traffic between clients and server:
```bash
# On Linux/macOS:
tcpdump -i any -n port 5555

# On Windows:
netsh trace start scenario=NetConnection level=verbose
```

---

## Checklist for Full Testing

- [ ] Server starts without errors
- [ ] Single client can connect
- [ ] Multiple clients can connect
- [ ] Game initializes with correct number of players
- [ ] Game state is synchronized across all clients
- [ ] Dice rolls are received by all clients
- [ ] Player movement is synchronized
- [ ] Board properties are displayed correctly
- [ ] Rent calculations are correct
- [ ] Player money updates correctly
- [ ] Game detects bankruptcies
- [ ] LAN connections work (not just localhost)
- [ ] Server handles client disconnections gracefully
- [ ] No memory leaks during extended play
