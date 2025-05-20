"""
Who Wants to Be a Millionaire - GUI Contestant Client
=================================================

Enhanced GUI interface with modern design and better user experience.
"""

import customtkinter as ctk
import json
import socket
import threading
from PIL import Image, ImageTk
from utils.config import *
from utils.logger import get_logger

logger = get_logger(__name__)

class WelcomeScreen(ctk.CTkToplevel):
    def __init__(self, parent, on_start):
        super().__init__(parent)
        
        # Store callback
        self.on_start = on_start
        
        # Configure window
        self.title("Who Wants to Be a Millionaire")
        self.geometry("800x600")
        self.resizable(False, False)
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create dark blue gradient background
        self.configure(fg_color=("#000C3C", "#000C3C"))
        
        # Create scrollable frame for content
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#000C3C",
            corner_radius=0
        )
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Title with classic Millionaire styling
        self.title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="WHO WANTS\nTO BE A\nMILLIONAIRE?",
            font=("Impact", 48, "bold"),
            text_color="#FFD700",
            justify="center"
        )
        self.title_label.pack(pady=(30, 20))
        
        # Decorative line
        self.line = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="#FFD700",
            height=2,
            width=600
        )
        self.line.pack(pady=20)
        
        # Rules with improved styling
        self.rules_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="#001166",
            corner_radius=15
        )
        self.rules_frame.pack(fill="x", padx=40, pady=20)
        
        self.rules_title = ctk.CTkLabel(
            self.rules_frame,
            text="GAME RULES",
            font=("Helvetica", 24, "bold"),
            text_color="#FFD700"
        )
        self.rules_title.pack(pady=(20, 10))
        
        rules_text = (
            "🎮 Answer 5 Progressive Questions\n"
            "💡 Use Your Lifelines Wisely:\n"
            "   📊 Ask the Audience\n"
            "   ✂️ 50:50\n"
            "💰 Win Up to $1,000,000!"
        )
        
        self.rules = ctk.CTkLabel(
            self.rules_frame,
            text=rules_text,
            font=("Helvetica", 18),
            justify="left",
            text_color="#FFFFFF"
        )
        self.rules.pack(pady=20)
        
        # Start button with enhanced styling
        self.start_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="START GAME",
            command=self.start_game,
            width=300,
            height=60,
            font=("Helvetica", 24, "bold"),
            fg_color="#FFD700",
            text_color="#000C3C",
            hover_color="#FFA500",
            corner_radius=30,
            border_width=2,
            border_color="#FFD700"
        )
        self.start_btn.pack(pady=30)
        
        # Ensure window is on top and focused
        self.attributes('-topmost', True)
        self.after(100, self.focus_force)
        self.grab_set()  # Make window modal
        
    def start_game(self):
        """Handle start game button click."""
        self.grab_release()  # Release modal state
        self.destroy()
        if self.on_start:
            self.on_start()

class MillionaireGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Who Wants to Be a Millionaire")
        self.geometry("1024x768")
        self.resizable(True, True)
        self.minsize(800, 600)
        
        # Set theme and styling
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Network setup
        self.host = GAME_SERVER_HOST
        self.port = GAME_SERVER_PORT
        self.socket = None
        self.connected = False
        
        # Game state
        self.current_question = None
        self.available_lifelines = []
        self.connection_attempts = 0
        self.MAX_RECONNECT_ATTEMPTS = 3
        
        # Create UI
        self.setup_ui()
        
        # Hide main window initially
        self.withdraw()
        
        # Show welcome screen after a short delay
        self.after(100, self.show_welcome_screen)
    
    def show_welcome_screen(self):
        """Show the welcome screen and ensure it's visible."""
        try:
            self.welcome = WelcomeScreen(self, self.on_game_start)
            self.welcome.protocol("WM_DELETE_WINDOW", self.on_welcome_close)  # Handle window close
            self.welcome.focus_force()  # Force focus on welcome screen
            self.welcome.grab_set()  # Make window modal
        except Exception as e:
            logger.error(f"Error showing welcome screen: {e}")
            self.destroy()  # Close the application if welcome screen fails
    
    def on_welcome_close(self):
        """Handle welcome screen close button."""
        self.welcome.destroy()
        self.destroy()  # Close the main application
    
    def on_game_start(self):
        """Called when user clicks Start Game on welcome screen."""
        self.deiconify()  # Show main window
        self.center_window()
        self.focus_force()  # Ensure main window has focus
        
    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        """Create and configure all UI elements with improved layout."""
        # Main container with grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main frame with padding and gradient background
        self.main_frame = ctk.CTkFrame(self, fg_color=("#1a1a2e", "#1a1a2e"))
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Header with game logo/title
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(20, 30), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        self.header = ctk.CTkLabel(
            header_frame,
            text="Who Wants to Be a Millionaire",
            font=("Helvetica", 32, "bold"),
            text_color="#FFD700"
        )
        self.header.grid(row=0, column=0)
        
        # Question section with distinct background
        self.question_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=("#2d2d3a", "#2d2d3a"),
            corner_radius=15
        )
        self.question_frame.grid(row=1, column=0, padx=40, pady=(0, 20), sticky="ew")
        self.question_frame.grid_columnconfigure(0, weight=1)
        
        self.question_label = ctk.CTkLabel(
            self.question_frame,
            text="Welcome to Who Wants to Be a Millionaire!",
            font=("Helvetica", 18),
            wraplength=800,
            pady=30
        )
        self.question_label.grid(row=0, column=0, padx=20)
        
        # Options grid (2x2)
        self.options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.options_frame.grid(row=2, column=0, padx=40, pady=(0, 20), sticky="ew")
        self.options_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.option_buttons = {}
        options = ['A', 'B', 'C', 'D']
        for i, opt in enumerate(options):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(
                self.options_frame,
                text=f"{opt}. ",
                font=("Helvetica", 16),
                command=lambda x=opt: self.submit_answer(x),
                height=70,
                fg_color=("#2d2d3a", "#2d2d3a"),
                hover_color=("#3d3d4a", "#3d3d4a"),
                corner_radius=10
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            self.option_buttons[opt] = btn
        
        # Lifelines with icons
        self.lifelines_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.lifelines_frame.grid(row=3, column=0, padx=40, pady=(0, 20), sticky="ew")
        self.lifelines_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.lifeline_buttons = {}
        
        # Ask the Audience lifeline
        self.lifeline_buttons['1'] = ctk.CTkButton(
            self.lifelines_frame,
            text="📊 Ask the Audience",
            command=lambda: self.use_lifeline('1'),
            width=200,
            height=50,
            font=("Helvetica", 16),
            fg_color=("#2d2d3a", "#2d2d3a"),
            hover_color=("#3d3d4a", "#3d3d4a")
        )
        self.lifeline_buttons['1'].grid(row=0, column=0, padx=10)
        
        # 50:50 lifeline
        self.lifeline_buttons['2'] = ctk.CTkButton(
            self.lifelines_frame,
            text="✂️ 50:50",
            command=lambda: self.use_lifeline('2'),
            width=200,
            height=50,
            font=("Helvetica", 16),
            fg_color=("#2d2d3a", "#2d2d3a"),
            hover_color=("#3d3d4a", "#3d3d4a")
        )
        self.lifeline_buttons['2'].grid(row=0, column=1, padx=10)
        
        # Game info section
        self.info_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=("#2d2d3a", "#2d2d3a"),
            corner_radius=15
        )
        self.info_frame.grid(row=4, column=0, padx=40, pady=(0, 20), sticky="ew")
        self.info_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Prize info (left column)
        self.prize_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.prize_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        self.prize_label = ctk.CTkLabel(
            self.prize_frame,
            text="Prize: $0",
            font=("Helvetica", 18, "bold"),
            text_color="#FFD700"
        )
        self.prize_label.pack()
        
        # Status info (right column)
        self.status_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.status_frame.grid(row=0, column=1, sticky="e", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready to start!",
            font=("Helvetica", 16)
        )
        self.status_label.pack()
        
        # Start button
        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="Connect to Server",
            command=self.start_game,
            width=200,
            height=50,
            font=("Helvetica", 16, "bold"),
            fg_color="#007AFF",
            hover_color="#0056B3"
        )
        self.start_button.grid(row=5, column=0, pady=20)
    
    def use_lifeline(self, lifeline_type):
        """Send lifeline request to server."""
        if self.socket and lifeline_type in self.available_lifelines:
            try:
                message = {
                    'type': CMD_LIFELINE,
                    'lifeline': lifeline_type
                }
                self.send_message(message)
                # Temporarily disable the button
                self.lifeline_buttons[lifeline_type].configure(state="disabled")
                self.update_status("Processing lifeline request...", "info")
            except Exception as e:
                logger.error(f"Error using lifeline: {e}")
                self.update_status("Failed to use lifeline!", "error")
                # Re-enable the button if request failed
                self.lifeline_buttons[lifeline_type].configure(state="normal")
    
    def show_lifeline_result(self, message):
        """Display lifeline results in a popup window."""
        try:
            popup = ctk.CTkToplevel(self)
            popup.title("Lifeline Result")
            popup.geometry("500x400")
            popup.grab_set()  # Make popup modal
            
            if message['type'] == RESP_LIFELINE and 'results' in message:  # Audience poll
                title = ctk.CTkLabel(popup, text="Audience Poll Results", font=("Helvetica", 20, "bold"))
                title.pack(pady=(20, 30))
                
                results_frame = ctk.CTkFrame(popup)
                results_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                for option, percentage in message['results'].items():
                    frame = ctk.CTkFrame(results_frame)
                    frame.pack(fill="x", pady=10)
                    
                    label = ctk.CTkLabel(frame, text=f"Option {option}:", font=("Helvetica", 16))
                    label.pack(side="left", padx=10)
                    
                    progress = ctk.CTkProgressBar(frame, width=300)
                    progress.pack(side="left", padx=10, expand=True)
                    progress.set(percentage / 100)
                    
                    value = ctk.CTkLabel(frame, text=f"{percentage}%", font=("Helvetica", 16))
                    value.pack(side="right", padx=10)
                
            elif message['type'] == RESP_LIFELINE and 'remaining' in message:  # 50:50
                title = ctk.CTkLabel(popup, text="50:50 Result", font=("Helvetica", 20, "bold"))
                title.pack(pady=(20, 30))
                
                info = ctk.CTkLabel(
                    popup,
                    text="Two options have been eliminated.\nRemaining options:",
                    font=("Helvetica", 16)
                )
                info.pack(pady=20)
                
                options_frame = ctk.CTkFrame(popup)
                options_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Disable eliminated options in main window
                for opt in self.option_buttons:
                    if opt not in message['remaining']:
                        self.option_buttons[opt].configure(state="disabled")
                
                for option, text in message['remaining'].items():
                    opt_label = ctk.CTkLabel(
                        options_frame,
                        text=f"{option}. {text}",
                        font=("Helvetica", 16),
                        fg_color="#2d2d2d",
                        corner_radius=8
                    )
                    opt_label.pack(pady=10, padx=20, fill="x")
            
            # Close button
            close_btn = ctk.CTkButton(
                popup,
                text="Close",
                command=popup.destroy,
                width=120,
                height=40
            )
            close_btn.pack(pady=20)
            
        except Exception as e:
            logger.error(f"Error showing lifeline result: {e}")
            self.update_status("Error displaying lifeline result", "error")
    
    def start_game(self):
        """Start a new game with improved error handling and reconnection logic."""
        if not self.connected and self.connection_attempts < self.MAX_RECONNECT_ATTEMPTS:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(5)  # 5 second timeout
                self.socket.connect((self.host, self.port))
                self.socket.settimeout(None)  # Reset timeout for normal operation
                self.connected = True
                self.connection_attempts = 0
                
                # Start message receiving thread
                self.receive_thread = threading.Thread(target=self.receive_messages)
                self.receive_thread.daemon = True
                self.receive_thread.start()
                
                self.start_button.configure(state="disabled")
                self.update_status("Connected! Waiting for first question...", "success")
                
            except socket.timeout:
                self.connection_attempts += 1
                self.update_status(f"Connection timeout! Attempt {self.connection_attempts}/{self.MAX_RECONNECT_ATTEMPTS}", "error")
                
            except ConnectionRefusedError:
                self.connection_attempts += 1
                self.update_status(
                    "Server connection refused! Please make sure the server is running.",
                    "error"
                )
                
            except Exception as e:
                logger.error(f"Connection error: {e}")
                self.update_status("Could not connect to server!", "error")
        elif self.connection_attempts >= self.MAX_RECONNECT_ATTEMPTS:
            self.update_status("Maximum connection attempts reached. Please try again later.", "error")
    
    def update_status(self, message, status_type="info"):
        """Update status with visual feedback."""
        colors = {
            "error": "#FF3B30",    # Red
            "success": "#34C759",  # Green
            "info": "#FFFFFF"      # White
        }
        self.status_label.configure(text=message, text_color=colors.get(status_type, "#FFFFFF"))
    
    def receive_messages(self):
        """Background thread to receive messages from server."""
        try:
            buffer = ""
            while True:
                chunk = self.socket.recv(BUFFER_SIZE).decode(ENCODING)
                if not chunk:
                    break
                
                buffer += chunk
                if '\n' in buffer:  # Found message delimiter
                    message = buffer.split('\n')[0]  # Get first complete message
                    buffer = ''.join(buffer.split('\n')[1:])  # Keep remaining data
                    
                    try:
                        parsed_message = json.loads(message)
                        self.after(0, self.handle_message, parsed_message)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing message: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            self.after(0, self.handle_disconnect)
    
    def handle_message(self, message):
        """Process received message and update UI accordingly."""
        try:
            if message['type'] == CMD_QUESTION:
                # Add a small delay before showing new question
                self.after(500, self.display_question, message)
                
            elif message['type'] == RESP_CORRECT:
                # Show success message and prepare for next question
                self.show_result("Correct! 🎉", message['prize'], "success")
                self.update_status("Preparing next question...", "info")
                # Clear current question display
                self.after(1000, self.clear_question_display)
                
            elif message['type'] == RESP_WRONG:
                self.show_result(
                    f"Wrong! Correct answer was {message['correct_answer']} ❌", 
                    message['prize'], 
                    "error"
                )
                self.after(2000, self.show_game_over, {
                    'type': CMD_GAMEOVER,
                    'message': "Game Over! Better luck next time!",
                    'prize': message['prize'],
                    'statistics': {
                        'questions_answered': message.get('question_number', 0),
                        'lifelines_used': len(AVAILABLE_LIFELINES) - len(self.available_lifelines)
                    }
                })
                
            elif message['type'] == CMD_GAMEOVER:
                self.after(500, self.show_game_over, message)
                
            elif message['type'] == RESP_LIFELINE:
                self.show_lifeline_result(message)
                
            elif message['type'] == RESP_ERROR:
                self.update_status(message['message'], "error")
                # Re-enable lifeline button if it failed
                if 'lifeline' in message:
                    self.lifeline_buttons[message['lifeline']].configure(state="normal")
                    
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self.update_status("Error processing server response", "error")
    
    def clear_question_display(self):
        """Clear current question display to prepare for next question."""
        self.question_label.configure(text="")
        for button in self.option_buttons.values():
            button.configure(text="", state="disabled")
            
    def display_question(self, message):
        """Display new question and options with smooth transition."""
        try:
            self.current_question = message
            self.available_lifelines = message['available_lifelines']
            
            # Update question with animation
            self.question_label.configure(
                text=f"Question {message['question_number']} of {message['total_questions']}:\n\n{message['question']}"
            )
            
            # Update options with slight delay between each
            for i, (opt, text) in enumerate(message['options'].items()):
                self.after(i * 200, lambda o=opt, t=text: self.option_buttons[o].configure(
                    text=f"{o}. {t}",
                    state="normal"
                ))
            
            # Update lifelines
            for lifeline_id, button in self.lifeline_buttons.items():
                button.configure(
                    state="normal" if lifeline_id in self.available_lifelines else "disabled"
                )
            
            # Update prize info
            self.prize_label.configure(
                text=f"Current Prize: ${message.get('prize', 0)}"
            )
            
            # Update status
            self.update_status("Choose your answer...", "info")
            
        except Exception as e:
            logger.error(f"Error displaying question: {e}")
            self.update_status("Error displaying question", "error")
    
    def submit_answer(self, answer):
        """Submit answer to server."""
        if self.socket and self.current_question:
            try:
                message = {
                    'type': CMD_ANSWER,
                    'answer': answer
                }
                self.send_message(message)
                
                # Disable buttons until next question
                for button in self.option_buttons.values():
                    button.configure(state="disabled")
            except Exception as e:
                logger.error(f"Error submitting answer: {e}")
                self.update_status("Failed to submit answer!", "error")
    
    def send_message(self, message):
        """Send message to server with error handling."""
        try:
            json_str = json.dumps(message) + '\n'  # Add newline as message delimiter
            self.socket.sendall(json_str.encode(ENCODING))  # Use sendall to ensure complete message is sent
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.handle_disconnect()
    
    def handle_disconnect(self):
        """Handle server disconnection."""
        self.connected = False
        self.socket = None
        self.update_status("Disconnected from server!", "error")
        self.start_button.configure(state="normal", text="Reconnect")
        
        # Reset game state
        self.current_question = None
        self.available_lifelines = []
        
        # Disable all buttons
        for button in self.option_buttons.values():
            button.configure(state="disabled")
        for button in self.lifeline_buttons.values():
            button.configure(state="disabled")
    
    def show_result(self, title, message, color):
        """Show result message with prize information."""
        try:
            # Create popup for result
            popup = ctk.CTkToplevel(self)
            popup.title("Question Result")
            popup.geometry("400x300")
            popup.resizable(False, False)
            
            # Center the popup
            popup.update_idletasks()
            width = popup.winfo_width()
            height = popup.winfo_height()
            x = (popup.winfo_screenwidth() // 2) - (width // 2)
            y = (popup.winfo_screenheight() // 2) - (height // 2)
            popup.geometry(f'{width}x{height}+{x}+{y}')
            
            # Configure popup
            popup.configure(fg_color=("#000C3C", "#000C3C"))
            popup.grab_set()  # Make popup modal
            
            # Result title
            title_label = ctk.CTkLabel(
                popup,
                text=title,
                font=("Helvetica", 24, "bold"),
                text_color="#FFD700" if "Correct" in title else "#FF3B30"
            )
            title_label.pack(pady=(40, 20))
            
            # Prize message
            prize_label = ctk.CTkLabel(
                popup,
                text=f"Prize: ${message}",
                font=("Helvetica", 20),
                text_color="#34C759"
            )
            prize_label.pack(pady=20)
            
            # Close button
            close_btn = ctk.CTkButton(
                popup,
                text="Continue",
                command=popup.destroy,
                width=150,
                height=40,
                font=("Helvetica", 16, "bold"),
                fg_color="#007AFF",
                hover_color="#0056B3"
            )
            close_btn.pack(pady=30)
            
        except Exception as e:
            logger.error(f"Error showing result: {e}")
            self.update_status("Error showing result", "error")
    
    def show_game_over(self, message):
        """Display game over screen with final results and play again option."""
        try:
            # Create game over popup
            popup = ctk.CTkToplevel(self)
            popup.title("Game Over")
            popup.geometry("500x400")
            popup.resizable(False, False)
            
            # Center the popup
            popup.update_idletasks()
            width = popup.winfo_width()
            height = popup.winfo_height()
            x = (popup.winfo_screenwidth() // 2) - (width // 2)
            y = (popup.winfo_screenheight() // 2) - (height // 2)
            popup.geometry(f'{width}x{height}+{x}+{y}')
            
            # Configure popup
            popup.configure(fg_color=("#000C3C", "#000C3C"))
            popup.grab_set()  # Make popup modal
            
            # Game over title
            title = ctk.CTkLabel(
                popup,
                text="🎮 Game Over",
                font=("Impact", 36, "bold"),
                text_color="#FFD700"
            )
            title.pack(pady=(40, 20))
            
            # Result message
            result = ctk.CTkLabel(
                popup,
                text=message['message'],
                font=("Helvetica", 20),
                text_color="#FFFFFF"
            )
            result.pack(pady=10)
            
            # Final prize
            prize = ctk.CTkLabel(
                popup,
                text=f"Final Prize: ${message['prize']}",
                font=("Helvetica", 24, "bold"),
                text_color="#34C759"
            )
            prize.pack(pady=20)
            
            # Statistics
            stats = message.get('statistics', {})
            stats_text = (
                f"Questions Answered: {stats.get('questions_answered', 0)}\n"
                f"Lifelines Used: {stats.get('lifelines_used', 0)}"
            )
            stats_label = ctk.CTkLabel(
                popup,
                text=stats_text,
                font=("Helvetica", 16),
                text_color="#FFFFFF"
            )
            stats_label.pack(pady=20)
            
            # Buttons frame
            buttons_frame = ctk.CTkFrame(popup, fg_color="transparent")
            buttons_frame.pack(pady=30)
            
            # Play Again button
            play_again_btn = ctk.CTkButton(
                buttons_frame,
                text="Play Again",
                command=lambda: self.restart_game(popup),
                width=150,
                height=40,
                font=("Helvetica", 16, "bold"),
                fg_color="#34C759",
                hover_color="#2FB344"
            )
            play_again_btn.pack(side="left", padx=10)
            
            # Quit button
            quit_btn = ctk.CTkButton(
                buttons_frame,
                text="Quit",
                command=lambda: self.quit_game(popup),
                width=150,
                height=40,
                font=("Helvetica", 16, "bold"),
                fg_color="#FF3B30",
                hover_color="#FF2419"
            )
            quit_btn.pack(side="left", padx=10)
            
            # Clear main window
            self.question_label.configure(text="")
            for button in self.option_buttons.values():
                button.configure(state="disabled", text="")
            for button in self.lifeline_buttons.values():
                button.configure(state="disabled")
            self.prize_label.configure(text=f"Final Prize: ${message['prize']}")
            self.status_label.configure(text="Game Over")
            
        except Exception as e:
            logger.error(f"Error showing game over: {e}")
            self.update_status("Error showing game over screen", "error")
    
    def restart_game(self, popup=None):
        """Restart the game by resetting the state and reconnecting."""
        try:
            if popup:
                popup.destroy()
            
            # Reset game state
            self.current_question = None
            self.available_lifelines = []
            self.connected = False
            self.connection_attempts = 0
            
            # Reset UI
            self.question_label.configure(text="")
            self.prize_label.configure(text="Prize: $0")
            self.status_label.configure(text="Ready to start!")
            
            for button in self.option_buttons.values():
                button.configure(text="", state="disabled")
            
            for button in self.lifeline_buttons.values():
                button.configure(state="disabled")
            
            # Close existing socket
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            
            # Start new game
            self.start_button.configure(state="normal", text="Connect to Server")
            self.start_game()
            
        except Exception as e:
            logger.error(f"Error restarting game: {e}")
            self.update_status("Error restarting game", "error")
    
    def quit_game(self, popup=None):
        """Quit the game and close the application."""
        try:
            if popup:
                popup.destroy()
            self.quit()
        except Exception as e:
            logger.error(f"Error quitting game: {e}")
            self.destroy()

if __name__ == "__main__":
    app = MillionaireGUI()
    app.mainloop() 