"""
Configuration settings for the Who Wants to Be a Millionaire game.
Contains network settings, game constants, and prize information.
"""

import os

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_FILE = os.path.join(BASE_DIR, 'data', 'questions.json')

# Network Configuration
GAME_SERVER_HOST = '127.0.0.1'
GAME_SERVER_PORT = 4337
LIFELINE_SERVER_HOST = '127.0.0.1'
LIFELINE_SERVER_PORT = 4338

# Game Configuration
MAX_QUESTIONS = 5
AVAILABLE_LIFELINES = ['1', '2']  # 1 for Ask Audience, 2 for 50:50
VALID_ANSWERS = ['A', 'B', 'C', 'D']

# Socket Configuration
BUFFER_SIZE = 1024
ENCODING = 'utf-8'
MAX_CONNECTIONS = 5
TIMEOUT_SECONDS = 30

# Prize Messages
PRIZE_MESSAGES = {
    0: "0",
    1: "1,000",
    2: "5,000",
    3: "10,000",
    4: "50,000",
    5: "100,000"
}

# Command Codes for Socket Communication
CMD_QUESTION = 'QUE'
CMD_ANSWER = 'ANS'
CMD_LIFELINE = 'LIF'
CMD_RESULT = 'RES'
CMD_GAMEOVER = 'END'

# Response Codes
RESP_CORRECT = 'COR'
RESP_WRONG = 'WRO'
RESP_LIFELINE = 'LIF'
RESP_ERROR = 'ERR'

# Lifeline Types
LIFELINE_AUDIENCE = '1'
LIFELINE_FIFTY = '2'

# Lifeline Names
LIFELINE_NAMES = {
    LIFELINE_AUDIENCE: '📊 Ask the Audience',
    LIFELINE_FIFTY: '✂️ 50:50'
} 