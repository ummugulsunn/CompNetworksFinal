"""
Who Wants to Be a Millionaire - Game Server
=========================================

This module implements the main game server for the Who Wants to Be a Millionaire game.
It acts as both a server (for contestants) and a client (for lifeline server).

Key Features:
------------
- TCP socket-based communication
- Multi-threaded to handle multiple contestants
- Question management and game flow control
- Lifeline processing through separate server
- Real-time game status monitoring

Network Configuration:
-------------------
- Listens on: 127.0.0.1:4337 (for contestants)
- Connects to: 127.0.0.1:4338 (lifeline server)

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
import threading
import time
from utils.config import *
from utils.logger import get_logger

logger = get_logger(__name__)

def send_message(socket, message):
    """
    Send a JSON message through the socket with proper encoding and termination.
    
    Args:
        socket (socket.socket): The socket connection to send through
        message (dict): The message dictionary to send
        
    Raises:
        Exception: If there's an error during message sending
    """
    try:
        json_str = json.dumps(message) + '\n'  # Add newline as message delimiter
        socket.sendall(json_str.encode(ENCODING))  # Use sendall to ensure complete message is sent
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise

def receive_message(socket):
    """
    Receive a JSON message from the socket.
    
    Args:
        socket: The socket to receive from
        
    Returns:
        dict: The received message as a dictionary
    """
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

class GameServer:
    def __init__(self):
        """Initialize the Game Server with game state and socket configuration."""
        self.host = GAME_SERVER_HOST
        self.port = GAME_SERVER_PORT
        self.server_socket = None
        self.lifeline_socket = None
        self.questions = self.load_questions()
        self.active_games = 0
        self.total_games_played = 0
        
    def load_questions(self):
        """Load questions from JSON file."""
        try:
            with open(QUESTIONS_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data['questions']
        except Exception as e:
            logger.error(f"Error loading questions: {e}")
            return []

    def connect_to_lifeline_server(self):
        """Establish connection to Lifeline Server."""
        try:
            self.lifeline_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.lifeline_socket.connect((LIFELINE_SERVER_HOST, LIFELINE_SERVER_PORT))
            logger.info("Connected to Lifeline Server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Lifeline Server: {e}")
            return False

    def start(self):
        """Start the Game Server and listen for contestant connections."""
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind and listen
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(MAX_CONNECTIONS)
            
            print(f"\n{'='*50}")
            print(f"🎮 Who Wants to Be a Millionaire - Game Server")
            print(f"{'='*50}")
            print(f"✨ Server started on {self.host}:{self.port}")
            print(f"📋 Loaded {len(self.questions)} questions")
            print(f"⏳ Waiting for contestants...")
            print(f"{'='*50}\n")
            
            # Start status display thread
            status_thread = threading.Thread(target=self.display_status, daemon=True)
            status_thread.start()
            
            while True:
                client_socket, address = self.server_socket.accept()
                self.active_games += 1
                self.total_games_played += 1
                
                # Start new thread for each contestant
                client_thread = threading.Thread(
                    target=self.handle_contestant,
                    args=(client_socket, address)
                )
                client_thread.start()
                
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def display_status(self):
        """Display real-time server status."""
        while True:
            print(f"\r🎮 Active Games: {self.active_games} | 📊 Total Games: {self.total_games_played}", end='')
            time.sleep(1)

    def handle_contestant(self, client_socket, address):
        """
        Handle contestant gameplay session.
        
        Args:
            client_socket (socket): Connected contestant socket
            address (tuple): Client address information
        """
        try:
            current_question = 0
            available_lifelines = AVAILABLE_LIFELINES.copy()
            logger.info(f"New contestant connected from {address}")
            
            # Main game loop
            while current_question < MAX_QUESTIONS:
                question = self.questions[current_question]
                
                # Add question number and prize info
                message = {
                    'type': CMD_QUESTION,
                    'question_number': current_question + 1,
                    'total_questions': MAX_QUESTIONS,
                    'question': question['question'],
                    'options': question['options'],
                    'available_lifelines': available_lifelines,
                    'prize': PRIZE_MESSAGES[current_question],
                    'next_prize': PRIZE_MESSAGES[current_question + 1] if current_question < MAX_QUESTIONS - 1 else None
                }
                
                # Add delay before sending new question
                time.sleep(0.5)
                send_message(client_socket, message)
                
                # Get contestant's response
                while True:
                    response = receive_message(client_socket)
                    if not response:
                        logger.info(f"Contestant {address} disconnected")
                        return
                    
                    # Handle lifeline request
                    if response['type'] == CMD_LIFELINE:
                        if response['lifeline'] not in available_lifelines:
                            error_msg = {
                                'type': RESP_ERROR,
                                'message': 'Lifeline not available',
                                'lifeline': response['lifeline']
                            }
                            send_message(client_socket, error_msg)
                            continue
                            
                        lifeline_result = self.process_lifeline(
                            response['lifeline'],
                            question['correct_answer'],
                            question['options']
                        )
                        
                        if lifeline_result:
                            available_lifelines.remove(response['lifeline'])
                            send_message(client_socket, lifeline_result)
                        else:
                            error_msg = {
                                'type': RESP_ERROR,
                                'message': 'Failed to process lifeline',
                                'lifeline': response['lifeline']
                            }
                            send_message(client_socket, error_msg)
                        continue
                    
                    # Handle answer submission
                    if response['type'] == CMD_ANSWER:
                        time.sleep(0.5)  # Add suspense
                        
                        if response['answer'] == question['correct_answer']:
                            result = {
                                'type': RESP_CORRECT,
                                'message': PRIZE_MESSAGES[current_question + 1],
                                'question_number': current_question + 1,
                                'total_questions': MAX_QUESTIONS,
                                'prize': PRIZE_MESSAGES[current_question + 1]
                            }
                            current_question += 1
                            send_message(client_socket, result)
                            time.sleep(1)  # Give time for UI update
                            break
                            
                        else:
                            result = {
                                'type': RESP_WRONG,
                                'message': PRIZE_MESSAGES[current_question],
                                'correct_answer': question['correct_answer'],
                                'explanation': question.get('explanation', 'Better luck next time!'),
                                'question_number': current_question + 1,
                                'prize': PRIZE_MESSAGES[current_question]
                            }
                            send_message(client_socket, result)
                            time.sleep(1)  # Give time for UI update
                            
                            # Send game over message
                            final_message = {
                                'type': CMD_GAMEOVER,
                                'message': "Game Over! Thanks for playing!",
                                'prize': PRIZE_MESSAGES[current_question],
                                'statistics': {
                                    'questions_answered': current_question,
                                    'lifelines_used': len(AVAILABLE_LIFELINES) - len(available_lifelines)
                                }
                            }
                            send_message(client_socket, final_message)
                            return
            
            # Player won the game
            final_message = {
                'type': CMD_GAMEOVER,
                'message': "🎉 Congratulations! You've won the game!",
                'prize': PRIZE_MESSAGES[MAX_QUESTIONS],
                'statistics': {
                    'questions_answered': MAX_QUESTIONS,
                    'lifelines_used': len(AVAILABLE_LIFELINES) - len(available_lifelines)
                }
            }
            send_message(client_socket, final_message)
            
        except Exception as e:
            logger.error(f"Error handling contestant {address}: {e}")
        finally:
            self.active_games -= 1
            client_socket.close()
            logger.info(f"Contestant {address} session ended")

    def process_lifeline(self, lifeline_type, correct_answer, options):
        """
        Process lifeline request through Lifeline Server.
        
        Args:
            lifeline_type (str): Type of lifeline ('1' for audience, '2' for 50:50)
            correct_answer (str): The correct option
            options (dict): All available options
            
        Returns:
            dict: Lifeline results
        """
        try:
            if not self.lifeline_socket or self.lifeline_socket._closed:
                if not self.connect_to_lifeline_server():
                    return None
            
            # Prepare request based on lifeline type
            request = {
                'type': 'audience' if lifeline_type == LIFELINE_AUDIENCE else '50-50',
                'correct_answer': correct_answer,
                'options': options
            }
            
            # Send request to lifeline server
            send_message(self.lifeline_socket, request)
            
            # Get response
            response = receive_message(self.lifeline_socket)
            if not response:
                return None
            
            # Format response for contestant
            response['type'] = RESP_LIFELINE
            return response
            
        except Exception as e:
            logger.error(f"Error processing lifeline: {e}")
            return None

if __name__ == "__main__":
    try:
        server = GameServer()
        server.start()
    except KeyboardInterrupt:
        print("\n\n🛑 Server shutting down...")
        print("👋 Goodbye!") 