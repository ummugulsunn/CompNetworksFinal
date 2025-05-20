"""
Who Wants to Be a Millionaire - Contestant Client
============================================

This module implements the contestant (player) client interface for the game.
It provides a colorful, interactive terminal-based UI and handles communication with the game server.

Key Features:
------------
- TCP socket-based communication with game server
- Colorful terminal user interface
- Interactive question/answer system
- Lifeline support
- Game progress tracking
- Multi-game session support

Network Configuration:
-------------------
- Connects to: 127.0.0.1:4337 (Game Server)

User Interface:
-------------
- Clear, color-coded display
- Question and options presentation
- Lifeline availability indicators
- Progress tracking
- Prize information
- Game statistics

Game Flow:
---------
1. Connect to game server
2. Display questions and options
3. Handle user input (answers/lifelines)
4. Show results and progress
5. Option to play multiple games

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
import sys
import time
import os
from colorama import init, Fore, Style, Back
from utils.config import *
from utils.logger import get_logger

# Initialize colorama for cross-platform colored output
init()

logger = get_logger(__name__)

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print game header."""
    clear_screen()
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"{Fore.CYAN}🎮 Who Wants to Be a Millionaire 🎮".center(60))
    print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")

def print_progress(question_number, total_questions, current_prize, next_prize=None):
    """Print progress information."""
    progress = f"Question {question_number} of {total_questions}"
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"{Fore.CYAN}{progress:^60}")
    print(f"{Fore.GREEN}Current Prize: {current_prize:^48}")
    if next_prize:
        print(f"{Fore.MAGENTA}Next Prize: {next_prize:^50}")
    print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")

def get_user_input(options, lifelines):
    """
    Get and validate user input for answers or lifelines.
    
    Args:
        options (dict): Available answer options
        lifelines (list): Available lifelines
        
    Returns:
        tuple: (input_type, value) where input_type is 'answer' or 'lifeline'
    """
    while True:
        # Show available options
        print(f"\n{Fore.YELLOW}Your options:")
        print(f"{Fore.CYAN}📝 To answer: Type A, B, C, or D{Style.RESET_ALL}")
        
        # Show lifeline options if available
        if lifelines:
            print(f"{Fore.MAGENTA}💡 For lifelines:")
            for lifeline in lifelines:
                print(f"   Type {lifeline} for {LIFELINE_NAMES[lifeline]}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Your choice: {Style.RESET_ALL}").upper().strip()
        
        # Validate input
        if choice in options:
            return 'answer', choice
        elif choice in lifelines:
            return 'lifeline', choice
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please try again.{Style.RESET_ALL}")

def send_message(socket, message):
    """
    Send a JSON message through the socket with proper encoding and termination.
    
    Args:
        socket: The socket to send through
        message: The message dictionary to send
    """
    try:
        # Add message terminator
        json_str = json.dumps(message) + '\n'
        socket.send(json_str.encode(ENCODING))
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
        data = socket.recv(BUFFER_SIZE).decode(ENCODING)
        if not data:
            return None
        return json.loads(data.strip())
    except Exception as e:
        logger.error(f"Error receiving message: {e}")
        raise

class Contestant:
    def __init__(self):
        """Initialize the Contestant client with socket configuration."""
        self.host = GAME_SERVER_HOST
        self.port = GAME_SERVER_PORT
        self.socket = None

    def connect(self):
        """Connect to the Game Server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logger.info("Connected to Game Server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Game Server: {e}")
            return False

    def start_game(self):
        """Main game loop that handles reconnection and multiple games."""
        while True:
            print_header()
            print(f"{Fore.CYAN}🎲 Starting new game...{Style.RESET_ALL}")
            time.sleep(1)
            self.play()
            
            # Ask if player wants to play again
            while True:
                choice = input(f"\n{Fore.YELLOW}Would you like to play again? (y/n): {Style.RESET_ALL}").lower()
                if choice in ['y', 'n']:
                    break
                print(f"{Fore.RED}Please enter 'y' for yes or 'n' for no.{Style.RESET_ALL}")
            
            if choice == 'n':
                print(f"\n{Fore.CYAN}👋 Thanks for playing! Goodbye!{Style.RESET_ALL}")
                break
            else:
                # Close existing socket before reconnecting
                if self.socket:
                    self.socket.close()
                    self.socket = None

    def play(self):
        """Single game session loop."""
        try:
            if not self.connect():
                print(f"{Fore.RED}❌ Failed to connect to the game server.{Style.RESET_ALL}")
                return

            print(f"{Fore.CYAN}🎮 Welcome to Who Wants to Be a Millionaire!{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Answer questions correctly to win prizes!{Style.RESET_ALL}")
            print()

            while True:
                # Receive message from server
                data = self.socket.recv(BUFFER_SIZE).decode(ENCODING)
                if not data:
                    break

                message = json.loads(data)
                
                if message['type'] == CMD_QUESTION:
                    self.handle_question(message)
                elif message['type'] == RESP_CORRECT:
                    print(f"\n{Fore.GREEN}✨ Correct! {message['message']}")
                    print(f"📊 Progress: Question {message['question_number']} of {message['total_questions']} completed!{Style.RESET_ALL}")
                elif message['type'] == RESP_WRONG:
                    print(f"\n{Fore.RED}❌ Wrong answer! The correct answer was {message['correct_answer']}")
                    print(f"💡 {message.get('explanation', '')}")
                    print(f"🏆 Game Over! {message['message']}{Style.RESET_ALL}")
                    break
                elif message['type'] == CMD_GAMEOVER:
                    print(f"\n{Fore.GREEN}{message['message']}")
                    print(f"🏆 Final Prize: {message['prize']}")
                    print(f"\n📊 Game Statistics:")
                    print(f"Questions Answered: {message['statistics']['questions_answered']}")
                    print(f"Lifelines Used: {message['statistics']['lifelines_used']}{Style.RESET_ALL}")
                    break
                elif message['type'] == RESP_LIFELINE:
                    self.display_lifeline_result(message)
                elif message['type'] == RESP_ERROR:
                    print(f"\n{Fore.RED}❌ Error: {message['message']}{Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Game error: {e}")
        finally:
            if self.socket:
                self.socket.close()
                self.socket = None

    def handle_question(self, message):
        """
        Display question and handle user input.
        
        Args:
            message (dict): Question data from server
        """
        while True:
            # Clear screen and show progress
            print_header()
            print_progress(
                message['question_number'],
                message['total_questions'],
                message['current_prize'],
                message['next_prize']
            )
            
            # Display question
            print(f"{Fore.YELLOW}❓ Question: {message['question']}{Style.RESET_ALL}")
            
            # Display options
            print(f"\n{Fore.CYAN}📝 Options:{Style.RESET_ALL}")
            for key, value in message['options'].items():
                print(f"{Fore.CYAN}{key}) {value}{Style.RESET_ALL}")
            
            # Display available lifelines
            lifelines = message['available_lifelines']
            if lifelines:
                print(f"\n{Fore.MAGENTA}💡 Available Lifelines:{Style.RESET_ALL}")
                for lifeline in lifelines:
                    print(f"{Fore.MAGENTA}{lifeline}) {LIFELINE_NAMES[lifeline]}{Style.RESET_ALL}")
            
            # Get and process user input
            input_type, choice = get_user_input(message['options'], lifelines)
            
            if input_type == 'answer':
                response = {
                    'type': CMD_ANSWER,
                    'answer': choice
                }
                send_message(self.socket, response)
                return
            else:  # lifeline
                response = {
                    'type': CMD_LIFELINE,
                    'lifeline': choice
                }
                send_message(self.socket, response)
                
                # Wait for lifeline result and display it
                lifeline_result = receive_message(self.socket)
                if lifeline_result and lifeline_result['type'] != RESP_ERROR:
                    self.display_lifeline_result(lifeline_result)
                    print(f"\n{Fore.GREEN}✨ After using the lifeline, please choose your answer.{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}❌ Error using lifeline. Please try again.{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def display_lifeline_result(self, message):
        """
        Display the results of using a lifeline.
        
        Args:
            message (dict): Lifeline result data
        """
        if message['type'] == 'audience':
            print(f"\n{Fore.MAGENTA}📊 Audience Poll Results:{Style.RESET_ALL}")
            # Sort by percentage for better visualization
            sorted_results = sorted(message['results'].items(), key=lambda x: x[1], reverse=True)
            for option, percentage in sorted_results:
                bar_length = int(percentage / 2)  # Scale to 50 characters max
                bar = '█' * bar_length + '░' * (50 - bar_length)
                print(f"{Fore.CYAN}{option}) {bar} {percentage}%{Style.RESET_ALL}")
        elif message['type'] == '50-50':
            print(f"\n{Fore.MAGENTA}✂️ Remaining Options:{Style.RESET_ALL}")
            for option, value in message['remaining'].items():
                print(f"{Fore.CYAN}{option}) {value}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Unknown lifeline result{Style.RESET_ALL}")

if __name__ == "__main__":
    contestant = Contestant()
    try:
        contestant.start_game()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.CYAN}👋 Thanks for playing! Goodbye!{Style.RESET_ALL}")
    finally:
        if contestant.socket:
            contestant.socket.close() 