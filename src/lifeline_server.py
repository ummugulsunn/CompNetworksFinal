"""
Who Wants to Be a Millionaire - Lifeline Server
============================================

This module implements the lifeline server that processes lifeline requests from the game server.
It provides two types of lifelines: "Ask the Audience" and "50:50".

Key Features:
------------
- TCP socket-based communication
- Processes "Ask the Audience" lifeline with realistic audience distribution
- Processes "50:50" lifeline by eliminating two wrong answers
- Stateless design for reliability

Network Configuration:
-------------------
- Listens on: 127.0.0.1:4338
- Accepts connections from: Game Server only

Lifeline Types:
-------------
1. Ask the Audience:
   - Generates realistic audience poll percentages
   - Biases results towards correct answer
   - Ensures percentages sum to 100%

2. 50:50:
   - Removes two incorrect options
   - Keeps correct answer and one random wrong answer
   - Returns remaining options to game server

Authors:
-------
- Ümmügülsün Türkmen
- Büşra Demirel

Course:
------
COE214 Computer Networks
Spring 2025
"""

import socket
import json
import random
from utils.config import *
from utils.logger import get_logger

logger = get_logger(__name__)

def send_message(socket, message):
    """Send a JSON message through the socket."""
    try:
        json_str = json.dumps(message) + '\n'  # Add newline as message delimiter
        socket.sendall(json_str.encode(ENCODING))  # Use sendall to ensure complete message is sent
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise

def receive_message(socket):
    """Receive a JSON message from the socket."""
    try:
        buffer = ""
        while True:
            chunk = socket.recv(BUFFER_SIZE).decode(ENCODING)
            if not chunk:
                return None
            
            buffer += chunk
            if '\n' in buffer:  # Found message delimiter
                message = buffer.split('\n')[0]  # Get first complete message
                return json.loads(message)
                
    except Exception as e:
        logger.error(f"Error receiving message: {e}")
        raise

class LifelineServer:
    def __init__(self):
        """Initialize the Lifeline Server with socket configuration."""
        self.host = LIFELINE_SERVER_HOST
        self.port = LIFELINE_SERVER_PORT
        self.server_socket = None

    def start(self):
        """Start the Lifeline Server and listen for connections."""
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind and listen
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(MAX_CONNECTIONS)
            
            print(f"\n{'='*50}")
            print(f"💡 Lifeline Server")
            print(f"{'='*50}")
            print(f"✨ Server started on {self.host}:{self.port}")
            print(f"⏳ Waiting for Game Server connection...")
            print(f"{'='*50}\n")
            
            while True:
                client_socket, address = self.server_socket.accept()
                logger.info(f"Connection from Game Server at {address}")
                self.handle_client(client_socket)
                
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def handle_client(self, client_socket):
        """
        Handle client connection and process lifeline requests.
        
        Args:
            client_socket (socket): Connected client socket
        """
        try:
            while True:
                # Receive lifeline request
                request = receive_message(client_socket)
                if not request:
                    break
                
                logger.debug(f"Received request: {request}")
                
                # Process lifeline request
                if request['type'] == 'audience':
                    response = self.process_audience_poll(request['correct_answer'])
                elif request['type'] == '50-50':
                    response = self.process_fifty_fifty(request['correct_answer'], request['options'])
                else:
                    response = {'error': 'Invalid lifeline type'}
                
                # Send response
                send_message(client_socket, response)
                
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def process_audience_poll(self, correct_answer):
        """
        Generate audience poll results with bias towards correct answer.
        
        Args:
            correct_answer (str): The correct option (A, B, C, or D)
            
        Returns:
            dict: Percentage distribution for each option
        """
        # Give correct answer higher probability
        percentages = {
            'A': random.randint(5, 20),
            'B': random.randint(5, 20),
            'C': random.randint(5, 20),
            'D': random.randint(5, 20)
        }
        
        # Boost correct answer
        percentages[correct_answer] = random.randint(40, 65)
        
        # Normalize to 100%
        total = sum(percentages.values())
        normalized = {k: int((v/total) * 100) for k, v in percentages.items()}
        
        # Ensure total is exactly 100%
        remainder = 100 - sum(normalized.values())
        normalized[correct_answer] += remainder
        
        return {
            'type': 'audience',
            'results': normalized
        }

    def process_fifty_fifty(self, correct_answer, options):
        """
        Remove two incorrect options for 50:50 lifeline.
        
        Args:
            correct_answer (str): The correct option (A, B, C, or D)
            options (dict): All available options
            
        Returns:
            dict: Two remaining options (correct + one wrong)
        """
        # Get all wrong answers
        wrong_answers = [opt for opt in options.keys() if opt != correct_answer]
        # Randomly select one wrong answer to keep
        keep_wrong = random.choice(wrong_answers)
        
        remaining = {
            correct_answer: options[correct_answer],
            keep_wrong: options[keep_wrong]
        }
        
        return {
            'type': '50-50',
            'remaining': remaining
        }

if __name__ == "__main__":
    try:
        server = LifelineServer()
        server.start()
    except KeyboardInterrupt:
        print("\n\n🛑 Server shutting down...")
        print("👋 Goodbye!") 