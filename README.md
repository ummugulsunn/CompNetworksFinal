# Who Wants to Be a Millionaire - Network Programming Project

## Course Information
- **Course:** COE214 Computer Networks
- **Department:** Computer Engineering
- **Semester:** Spring 2025


## Project Team
- **Team Members:**
  - Ümmügülsün Türkmen
  - *****

## Project Overview
This project implements a networked version of "Who Wants to Be a Millionaire" using TCP socket programming. The implementation consists of three separate processes that communicate over a network:

### Components
1. **Contestant (Client)**
   - Connects to Game Server
   - Modern GUI interface for gameplay
   - Handles user interactions and lifeline requests

2. **Game Server (Server + Client)**
   - Manages game logic and question flow
   - Communicates with Contestant
   - Connects to Lifeline Server when needed
   - Handles prize management

3. **Lifeline Server (Server)**
   - Processes lifeline requests
   - Provides "Ask the Audience" and "50:50" functionality

## Technical Specifications

### Network Configuration
- Game Server: localhost (127.0.0.1), port 4337
- Lifeline Server: localhost (127.0.0.1), port 4338
- Protocol: TCP
- Encoding: UTF-8

### Game Features
- 5 progressive Computer Networks questions
- 2 lifelines:
  - Ask the Audience (percentage distribution)
  - 50:50 (eliminates two wrong answers)
- Progressive prize system
- Real-time game status monitoring

## Project Structure
```
project/
├── src/
│   ├── contestant_gui.py   # GUI Client implementation
│   ├── game_server.py      # Main game server
│   ├── lifeline_server.py  # Lifeline server
│   ├── utils/
│   │   ├── config.py       # Configuration settings
│   │   └── logger.py       # Logging utilities
│   └── data/
│       └── questions.json  # Question database
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Technologies Used
- Python 3.8+
- CustomTkinter for modern GUI
- TCP Sockets for network communication
- JSON for message passing
- Logging for error tracking

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Required packages:
  ```bash
  pip install -r requirements.txt
  ```

### Running the Application
Start the components in the following order:

1. Start Lifeline Server:
```bash
cd src
python3 lifeline_server.py
```

2. Start Game Server:
```bash
cd src
python3 game_server.py
```

3. Start Contestant GUI:
```bash
cd src
python3 contestant_gui.py
```

## Network Communication Analysis
The project's network communication can be analyzed using Wireshark:
1. Open Wireshark
2. Capture on loopback interface (lo0)
3. Filter: `tcp.port == 4337 || tcp.port == 4338`
4. Observe:
   - TCP connection establishment
   - JSON message exchange
   - Lifeline request/response flow
   - Game termination sequence

## Implementation Details

### Message Protocol
All communication uses JSON messages with the following types:
- Question delivery (QUE)
- Answer submission (ANS)
- Lifeline requests (LIF)
- Game results (RES)
- Game over (END)

Message Format Examples:
```json
// Question Message
{
    "type": "QUE",
    "question": "What protocol operates at the transport layer?",
    "options": ["HTTP", "TCP", "IP", "Ethernet"],
    "level": 1,
    "prize": 1000
}

// Answer Message
{
    "type": "ANS",
    "answer": "TCP",
    "level": 1
}

// Lifeline Request
{
    "type": "LIF",
    "lifeline_type": "50:50",
    "question_id": 1
}

// Game Result
{
    "type": "RES",
    "correct": true,
    "prize": 1000,
    "message": "Correct! You've won $1,000!"
}

// Game Over
{
    "type": "END",
    "final_prize": 50000,
    "message": "Congratulations! You're walking away with $50,000!"
}
```

### Prize Structure
Progressive prize system with following levels:
```
Level 0: $0
Level 1: $1,000
Level 2: $5,000
Level 3: $10,000
Level 4: $50,000
Level 5: $100,000
```

### Error Handling
- Network connection failures
- Invalid user inputs
- Lifeline server unavailability
- Game state inconsistencies

## Testing
The application has been tested for:
- Normal gameplay flow
- Lifeline functionality
- Network error scenarios
- GUI responsiveness
- Multi-client support

## Future Improvements
Potential areas for enhancement:
- Database integration for questions
- Additional lifeline types
- Multiplayer support
- Score history tracking
- Sound effects and animations

## Acknowledgments
- CustomTkinter for modern UI components
- Beej's Guide to Network Programming
- Course materials and lectures

## License
This project is created for educational purposes as part of the COE214 Computer Networks course.
