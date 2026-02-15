import tkinter as tk
from tkinter import ttk, scrolledtext, font
import threading
import datetime
import speech_recognition as sr
import pyttsx3
import wikipedia
import webbrowser
import os
import pywhatkit
import math 
import pyjokes
import pyautogui
import requests
import psutil
import time
import subprocess
import ctypes
import winshell
import platform
import comtypes
import wmi
import re
import pythoncom 
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from word2number import w2n

# =============== CONFIG ===============
WEATHER_API_KEY = "afb5841b0ed3626f7e827aee157f5ce0"
NEWS_API_KEY = "60055535e6ef42c7b4182e3b8be4e712"

contacts = {
    "me": "+919058401601",
    "a": "+918865038877",
    "x": "+919105611055"
}
# ======================================

NUMBER_WORDS = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",
    "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
    "hundred", "thousand", "and", "minus"
}

class VetoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("V E T O  -  AI VOICE ASSISTANT")
        self.root.geometry("1100x700")
        self.root.configure(bg='#0a0e27')
        
        self.is_listening = False
        self.continuous_mode = False
        self.rotation_angle = 0
        self.pulse_size = 0
        self.pulse_direction = 1
        self.tts_lock = threading.Lock()
        
        # Colors for different states
        self.color_idle = '#00d4ff'      # Cyan
        self.color_listening = '#ff00ff' # Magenta
        self.color_speaking = '#00ff88'  # Green
        self.current_color = self.color_idle
        
        # Check available fonts
        available_fonts = font.families()
        self.title_font = 'Consolas' if 'Consolas' in available_fonts else 'Courier New'
        self.text_font = 'Consolas' if 'Consolas' in available_fonts else 'Courier New'
        
        self.create_widgets()
        self.animate_logo()
        
        # Auto-greet on startup
        self.root.after(1500, self.startup_greeting)
        
    def startup_greeting(self):
        """Greet user on startup"""
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            greeting = "Good Morning!"
        elif 12 <= hour < 18:
            greeting = "Good Afternoon!"
        else:
            greeting = "Good Evening!"
        
        welcome_msg = f"{greeting} I am VETO, your advanced AI assistant. Ready to serve you."
        self.add_message("VETO", welcome_msg)
        
        # Speak in separate thread
        def speak_greeting():
            self.speak(welcome_msg)
        
        thread = threading.Thread(target=speak_greeting, daemon=True)
        thread.start()
    
    def speak(self, text):
        """Text-to-speech with proper threading"""
        print(f"VETO: {text}")
        
        def _speak():
            with self.tts_lock:
                try:
                    pythoncom.CoInitialize()
                    self.root.after(0, lambda: self.set_visual_state('speaking'))
                    
                    # Initialize engine fresh each time for reliability
                    engine = pyttsx3.init()
                    
                    try:
                        engine.setProperty(
                            'voice',
                            'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0'
                        )
                    except:
                        # Use default voice if David is not available
                        voices = engine.getProperty('voices')
                        if voices:
                            engine.setProperty('voice', voices[0].id)
                    
                    engine.setProperty('rate', 200)
                    engine.setProperty('volume', 1.0)
                    
                    spaced_text = "  ".join(text.split())
                    engine.say(spaced_text)
                    engine.runAndWait()
                    engine.stop()
                    
                except Exception as e:
                    print(f"Error speaking: {e}")
                finally:
                    pythoncom.CoUninitialize()
                    # Reset visual state
                    if self.continuous_mode:
                        self.root.after(0, lambda: self.set_visual_state('listening'))
                    else:
                        self.root.after(0, lambda: self.set_visual_state('idle'))
        
        # Run in thread
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main_container = tk.Frame(self.root, bg='#0a0e27')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Logo and visualization
        left_panel = tk.Frame(main_container, bg='#0a0e27', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20)
        left_panel.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            left_panel,
            text="V E T O",
            font=(self.title_font, 36, 'bold'),
            bg='#0a0e27',
            fg='#00d4ff'
        )
        title_label.pack(pady=(20, 5))
        
        subtitle = tk.Label(
            left_panel,
            text="━━━ AI VOICE ASSISTANT ━━━",
            font=(self.text_font, 10),
            bg='#0a0e27',
            fg='#888888'
        )
        subtitle.pack(pady=(0, 20))
        
        # Canvas for rotating logo
        self.canvas = tk.Canvas(
            left_panel,
            width=350,
            height=350,
            bg='#0a0e27',
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        
        # Status indicators
        status_frame = tk.Frame(left_panel, bg='#0a0e27')
        status_frame.pack(pady=20)
        
        self.status_label = tk.Label(
            status_frame,
            text="[ STANDBY ]",
            font=(self.text_font, 12, 'bold'),
            bg='#0a0e27',
            fg='#00d4ff'
        )
        self.status_label.pack(pady=5)
        
        self.mode_label = tk.Label(
            status_frame,
            text="CONTINUOUS MODE: OFFLINE",
            font=(self.text_font, 9),
            bg='#0a0e27',
            fg='#ff6b6b'
        )
        self.mode_label.pack(pady=5)
        
        # Control buttons
        btn_frame = tk.Frame(left_panel, bg='#0a0e27')
        btn_frame.pack(pady=20)
        
        self.toggle_button = tk.Button(
            btn_frame,
            text="⚡ ACTIVATE LISTENING ⚡",
            font=(self.text_font, 11, 'bold'),
            bg='#00ff88',
            fg='#000000',
            relief=tk.FLAT,
            padx=20,
            pady=15,
            command=self.toggle_continuous_mode,
            cursor='hand2',
            activebackground='#00cc66'
        )
        self.toggle_button.pack(pady=5)
        
        clear_btn = tk.Button(
            btn_frame,
            text="⟳ RESET INTERFACE",
            font=(self.text_font, 10),
            bg='#1a1a2e',
            fg='#ff6b6b',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.clear_chat,
            cursor='hand2',
            activebackground='#2a2a3e'
        )
        clear_btn.pack(pady=5)
        
        # Right panel - Chat interface
        right_panel = tk.Frame(main_container, bg='#0a0e27')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20)
        
        # Chat header
        chat_header = tk.Frame(right_panel, bg='#1a1a2e', height=50)
        chat_header.pack(fill=tk.X, pady=(0, 10))
        chat_header.pack_propagate(False)
        
        chat_title = tk.Label(
            chat_header,
            text="⟨ NEURAL INTERFACE ⟩",
            font=(self.text_font, 14, 'bold'),
            bg='#1a1a2e',
            fg='#00d4ff'
        )
        chat_title.pack(expand=True)
        
        # Chat area with cyberpunk border
        chat_container = tk.Frame(right_panel, bg='#00d4ff', bd=0)
        chat_container.pack(fill=tk.BOTH, expand=True)
        
        chat_inner = tk.Frame(chat_container, bg='#0f3460')
        chat_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.chat_area = scrolledtext.ScrolledText(
            chat_inner,
            wrap=tk.WORD,
            font=(self.text_font, 11),
            bg='#0f3460',
            fg='#ffffff',
            insertbackground='#00d4ff',
            relief=tk.FLAT,
            padx=15,
            pady=15,
            selectbackground='#1a4d7a'
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)
        
        # Configure tags
        self.chat_area.tag_config('user', foreground='#ff00ff', font=(self.text_font, 11, 'bold'))
        self.chat_area.tag_config('bot', foreground='#00ff88', font=(self.text_font, 11, 'bold'))
        self.chat_area.tag_config('time', foreground='#666666', font=(self.text_font, 8))
        self.chat_area.tag_config('system', foreground='#00d4ff', font=(self.text_font, 10, 'italic'))
        
        # Input area
        input_container = tk.Frame(right_panel, bg='#00d4ff')
        input_container.pack(fill=tk.X, pady=(10, 0))
        
        input_frame = tk.Frame(input_container, bg='#1a1a2e')
        input_frame.pack(fill=tk.X, padx=2, pady=2)
        
        self.input_entry = tk.Entry(
            input_frame,
            font=(self.text_font, 12),
            bg='#1a1a2e',
            fg='#00d4ff',
            insertbackground='#00d4ff',
            relief=tk.FLAT,
            bd=10
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)
        self.input_entry.bind('<Return>', lambda e: self.send_text_command())
        
        send_btn = tk.Button(
            input_frame,
            text="→ SEND",
            font=(self.text_font, 11, 'bold'),
            bg='#00d4ff',
            fg='#000000',
            relief=tk.FLAT,
            padx=25,
            command=self.send_text_command,
            cursor='hand2',
            activebackground='#00a8cc'
        )
        send_btn.pack(side=tk.RIGHT)
        
    def draw_rotating_logo(self):
        """Draw the animated rotating VETO logo"""
        self.canvas.delete("all")
        
        cx, cy = 175, 175  # Center
        
        # Outer pulsing glow
        glow_radius = 140 + self.pulse_size
        for i in range(5, 0, -1):
            alpha_color = self.get_gradient_color(self.current_color, i * 15)
            self.canvas.create_oval(
                cx - glow_radius - i*8, cy - glow_radius - i*8,
                cx + glow_radius + i*8, cy + glow_radius + i*8,
                outline=alpha_color, width=2
            )
        
        # Rotating outer ring segments
        num_segments = 12
        for i in range(num_segments):
            angle = self.rotation_angle + (i * 30)
            self.draw_arc_segment(cx, cy, 130, angle, 25, self.current_color, 4)
        
        # Middle ring (counter-rotating)
        for i in range(8):
            angle = -self.rotation_angle * 1.5 + (i * 45)
            self.draw_arc_segment(cx, cy, 100, angle, 35, self.current_color, 3)
        
        # Inner ring
        for i in range(6):
            angle = self.rotation_angle * 2 + (i * 60)
            self.draw_arc_segment(cx, cy, 70, angle, 50, self.current_color, 2)
        
        # Center circle with gradient
        for i in range(15, 0, -1):
            color = self.get_gradient_color(self.current_color, i * 4)
            self.canvas.create_oval(
                cx - i*3, cy - i*3,
                cx + i*3, cy + i*3,
                fill=color, outline=''
            )
        
        # VETO text in center
        self.canvas.create_text(
            cx, cy,
            text="VETO",
            font=(self.title_font, 28, 'bold'),
            fill="#EA0C0C"
        )
        
        # Corner decorations
        self.draw_corner_brackets(10, 10, 30, self.current_color)
        self.draw_corner_brackets(340, 10, 30, self.current_color, flip_x=True)
        self.draw_corner_brackets(10, 340, 30, self.current_color, flip_y=True)
        self.draw_corner_brackets(340, 340, 30, self.current_color, flip_x=True, flip_y=True)
        
    def draw_arc_segment(self, cx, cy, radius, start_angle, extent, color, width):
        """Draw an arc segment"""
        x1 = cx - radius
        y1 = cy - radius
        x2 = cx + radius
        y2 = cy + radius
        self.canvas.create_arc(
            x1, y1, x2, y2,
            start=start_angle,
            extent=extent,
            outline=color,
            width=width,
            style=tk.ARC
        )
    
    def draw_corner_brackets(self, x, y, size, color, flip_x=False, flip_y=False):
        """Draw corner bracket decorations"""
        offset_x = -1 if flip_x else 1
        offset_y = -1 if flip_y else 1
        
        # Horizontal line
        self.canvas.create_line(
            x, y,
            x + (size * offset_x), y,
            fill=color, width=2
        )
        # Vertical line
        self.canvas.create_line(
            x, y,
            x, y + (size * offset_y),
            fill=color, width=2
        )
    
    def get_gradient_color(self, hex_color, alpha):
        """Create gradient effect by adjusting opacity/brightness"""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        factor = max(0, min(100, alpha)) / 100
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def animate_logo(self):
        """Animate the rotating logo"""
        self.rotation_angle = (self.rotation_angle + 2) % 360
        
        # Pulse effect
        self.pulse_size += self.pulse_direction * 0.5
        if self.pulse_size > 10:
            self.pulse_direction = -1
        elif self.pulse_size < 0:
            self.pulse_direction = 1
        
        self.draw_rotating_logo()
        self.root.after(50, self.animate_logo)
    
    def set_visual_state(self, state):
        """Change colors based on state"""
        if state == 'idle':
            self.current_color = self.color_idle
        elif state == 'listening':
            self.current_color = self.color_listening
        elif state == 'speaking':
            self.current_color = self.color_speaking
    
    def add_message(self, sender, message):
        """Add message to chat area"""
        self.chat_area.config(state=tk.NORMAL)
        
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        
        if sender == "You":
            self.chat_area.insert(tk.END, f"┌─[ USER ]─[ {timestamp} ]\n", 'system')
            self.chat_area.insert(tk.END, f"│ {message}\n", 'user')
            self.chat_area.insert(tk.END, f"└{'─' * 50}\n\n", 'system')
        else:
            self.chat_area.insert(tk.END, f"┌─[ VETO ]─[ {timestamp} ]\n", 'system')
            self.chat_area.insert(tk.END, f"│ {message}\n", 'bot')
            self.chat_area.insert(tk.END, f"└{'─' * 50}\n\n", 'system')
        
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def update_status(self, text, color='#00ff00'):
        """Update status label"""
        self.status_label.config(text=f"[ {text.upper()} ]", fg=color)
    
    def listen(self):
        """Listen for voice input"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            self.set_visual_state('listening')
            self.update_status("LISTENING", '#ff00ff')
            r.pause_threshold = 1
            r.energy_threshold = 4000
            audio = r.listen(source)
        try:
            self.update_status("PROCESSING", '#00d4ff')
            query = r.recognize_google(audio, language="en-in")
            print(f"You said: {query}")
            return query.lower()
        except Exception as e:
            return "none"
    
    def toggle_continuous_mode(self):
        """Toggle continuous listening mode"""
        if not self.continuous_mode:
            # Start continuous mode
            self.continuous_mode = True
            self.toggle_button.config(bg='#ff6b6b', text='⏹ DEACTIVATE LISTENING ⏹')
            self.mode_label.config(text='CONTINUOUS MODE: ⚡ ONLINE ⚡', fg='#00ff88')
            self.set_visual_state('listening')
            self.add_message("VETO", "Neural interface activated. Continuous listening mode engaged.")
            
            # Speak confirmation
            threading.Thread(target=lambda: self.speak("Continuous listening mode engaged."), daemon=True).start()
            
            # Start listening thread
            thread = threading.Thread(target=self.continuous_listening_loop, daemon=True)
            thread.start()
        else:
            # Stop continuous mode
            self.continuous_mode = False
            self.toggle_button.config(bg='#00ff88', text='⚡ ACTIVATE LISTENING ⚡')
            self.mode_label.config(text='CONTINUOUS MODE: OFFLINE', fg='#ff6b6b')
            self.update_status("STANDBY", '#00d4ff')
            self.set_visual_state('idle')
            self.add_message("VETO", "Continuous listening mode disengaged.")
    
    def continuous_listening_loop(self):
        """Continuous listening loop"""
        while self.continuous_mode:
            query = self.listen()
            
            if query != "none":
                self.root.after(0, lambda q=query: self.add_message("You", q))
                self.process_command(query)
                
                # Check for exit command
                if any(term in query for term in ["exit", "quit", "bye", "goodbye", "kill yourself", "kill", "die"]):
                    break
            
            time.sleep(0.5)
        
        if self.continuous_mode:
            self.continuous_mode = False
            self.root.after(0, lambda: self.toggle_button.config(bg='#00ff88', text='⚡ ACTIVATE LISTENING ⚡'))
            self.root.after(0, lambda: self.mode_label.config(text='CONTINUOUS MODE: OFFLINE', fg='#ff6b6b'))
    
    def send_text_command(self):
        """Process text command"""
        query = self.input_entry.get().strip()
        if not query:
            return
        
        self.input_entry.delete(0, tk.END)
        self.add_message("You", query)
        
        # Process in thread
        thread = threading.Thread(target=self.process_command, args=(query.lower(),))
        thread.daemon = True
        thread.start()
    
    def clear_chat(self):
        """Clear chat area"""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self.add_message("VETO", "Interface reset complete. Standing by for commands.")
    
    def bot_response(self, text):
        """Add bot response and speak"""
        self.add_message("VETO", text)
        self.speak(text)
        if not self.continuous_mode:
            self.update_status("STANDBY", '#00d4ff')
    
    # ========== ALL YOUR ORIGINAL FUNCTIONS ==========
    
    def extract_number(self, query):
        if not query:
            return None
        m = re.search(r'\d+', query)
        if m:
            try:
                return int(m.group())
            except:
                pass
        tokens = re.findall(r"[A-Za-z]+", query.lower())
        num_tokens = [t for t in tokens if t in NUMBER_WORDS]
        if num_tokens:
            joined = " ".join(num_tokens)
            try:
                return w2n.word_to_num(joined)
            except Exception:
                try:
                    return w2n.word_to_num(" ".join(num_tokens[-3:]))
                except Exception:
                    pass
        try:
            last_words = " ".join(tokens[-4:])
            return w2n.word_to_num(last_words)
        except Exception:
            return None
    
    def tell_time(self):
        self.bot_response(f"The time is {datetime.datetime.now().strftime('%H:%M')}")
    
    def tell_date(self):
        today = datetime.date.today()
        self.bot_response(today.strftime("Today is %A, %B %d, %Y"))
    
    def search_wikipedia(self, query):
        topic = query.replace("wikipedia", "").replace("search", "").strip()
        if topic:
            try:
                results = wikipedia.summary(topic, sentences=2)
                self.bot_response(f"According to Wikipedia, {results}")
            except Exception:
                self.bot_response("Could not fetch from Wikipedia.")
        else:
            self.bot_response("Please tell me what to search.")
    
    def search_google(self, query):
        query_to_search = query.replace("google", "").replace("search", "").strip()
        if query_to_search:
            url = f"https://www.google.com/search?q={query_to_search.replace(' ', '+')}"
            webbrowser.open(url)
            self.bot_response(f"Searching Google for {query_to_search}.")
        else:
            self.bot_response("Please tell me what to search.")
    
    def open_website(self, query):
        common_websites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.twitter.com",
            "linkedin": "https://www.linkedin.com",
            "github": "https://www.github.com",
            "gmail": "https://mail.google.com"
        }
        for name, url in common_websites.items():
            if name in query:
                webbrowser.open(url)
                self.bot_response(f"Opening {name}.")
                return
        self.bot_response("Sorry, I don't have that website in my list.")
    
    def play_song(self, query):
        song = query.replace("play", "").replace("song", "").replace("on youtube", "").strip()
        if song:
            pywhatkit.playonyt(song)
            self.bot_response(f"Playing {song} on YouTube.")
        else:
            self.bot_response("I didn't hear a song name.")
    
    def remember_note(self, query):
        note = query.replace("remember", "").strip()
        if note:
            with open("notes.txt", "a") as f:
                f.write(note + "\n")
            self.bot_response("I will remember that.")
        else:
            self.bot_response("I didn't hear anything to remember.")
    
    def recall_notes(self):
        if os.path.exists("notes.txt"):
            with open("notes.txt", "r") as f:
                notes = f.read().strip()
            if notes:
                self.bot_response("You told me to remember this: " + notes)
            else:
                self.bot_response("You have no notes.")
        else:
            self.bot_response("You have no notes.")
    
    def clear_notes(self):
        if os.path.exists("notes.txt"):
            open("notes.txt", "w").close()
            self.bot_response("All notes have been cleared.")
        else:
            self.bot_response("You have no notes to clear.")
    
    def todo_add(self, query):
        task = query.replace("add task", "").replace("add a task", "").replace("atask", "").strip()
        if task:
            with open("todo.txt", "a") as f:
                f.write(task + "\n")
            self.bot_response("Task added to your to-do list.")
        else:
            self.bot_response("I didn't hear a task to add.")
    
    def todo_show(self):
        if os.path.exists("todo.txt"):
            with open("todo.txt", "r") as f:
                tasks = f.read().strip()
            if tasks:
                self.bot_response("Here are your tasks: " + tasks)
            else:
                self.bot_response("Your to-do list is empty.")
        else:
            self.bot_response("Your to-do list is empty.")
    
    def get_weather(self, query):
        city = query.replace("weather in", "").replace("weather", "").strip()
        if not city:
            city = "Delhi"
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            data = requests.get(url).json()
            if data.get("cod") != 200:
                self.bot_response("Couldn't find that city.")
                return
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            self.bot_response(f"The weather in {city} is {desc} with {temp} degree Celsius.")
        except Exception:
            self.bot_response("Couldn't fetch weather.")
    
    def system_status(self):
        battery = psutil.sensors_battery()
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        response = (f"Battery is at {battery.percent} percent. "
                    f"Power is {'plugged in' if battery.power_plugged else 'not plugged in'}. "
                    f"CPU usage is {cpu} percent and RAM usage is {ram} percent.")
        self.bot_response(response)
    
    def take_screenshot(self):
        try:
            img = pyautogui.screenshot()
            img.save("screenshot.png")
            self.bot_response("Screenshot saved.")
        except Exception:
            self.bot_response("Failed to take a screenshot.")
    
    def get_news(self):
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
            response = requests.get(url)
            articles = response.json()["articles"][:5]
            headlines = ["Here are the top headlines:"]
            for i, article in enumerate(articles, 1):
                headlines.append(f"Headline {i}. {article['title']}")
            self.bot_response(" ".join(headlines))
        except Exception:
            self.bot_response("Couldn't fetch news.")
    
    def calculate(self, query):
        query = query.lower()
        query = (query.replace("plus", "+")
                       .replace("add", "+")
                       .replace("minus", "-")
                       .replace("subtract", "-")
                       .replace("into", "*")
                       .replace("multiply", "*")
                       .replace("multiplied by", "*")
                       .replace("times", "*")
                       .replace("x", "*")
                       .replace("divided by", "/")
                       .replace("divide", "/")
                       .replace("by", "/")
                       .replace("power", "**")
                       .replace("to the power of", "**")
                       .replace("^", "**"))

        for word in ["calculate", "what is", "find", "answer", "result", "the", "of"]:
            query = query.replace(word, "").strip()

        try:
            if "square root" in query:
                num = float(query.split("square root")[-1].strip())
                result = math.sqrt(num)
                self.bot_response(f"The square root of {num} is {result}")
            elif "cube root" in query:
                num = float(query.split("cube root")[-1].strip())
                result = round(num ** (1/3), 6)
                self.bot_response(f"The cube root of {num} is {result}")
            elif "square of" in query:
                num = float(query.split("square of")[-1].strip())
                result = num ** 2
                self.bot_response(f"The square of {num} is {result}")
            elif "cube of" in query:
                num = float(query.split("cube of")[-1].strip())
                result = num ** 3
                self.bot_response(f"The cube of {num} is {result}")
            elif "%" in query or "percent" in query:
                query = query.replace("percent", "%")
                if "of" in query:
                    parts = query.split("of")
                    percent_val = float(parts[0].replace("%", "").strip())
                    total_val = float(parts[1].strip())
                    result = (percent_val / 100) * total_val
                    self.bot_response(f"{percent_val} percent of {total_val} is {result}")
                else:
                    expr = query.replace("%", "/100")
                    result = eval(expr)
                    self.bot_response(f"The answer is {result}")
            else:
                result = eval(query)
                self.bot_response(f"The answer is {result}")
        except Exception as e:
            self.bot_response("Sorry, I couldn't calculate that.")
    
    def set_system_volume(self, level):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol = ctypes.cast(interface, comtypes.POINTER(IAudioEndpointVolume))
            level_to_set = min(100, max(0, int(level)))
            vol.SetMasterVolumeLevelScalar(level_to_set / 100.0, None)
            self.bot_response(f"Volume set to {level_to_set} percent.")
        except Exception:
            self.bot_response("Sorry, I was unable to set the volume.")
    
    def set_brightness(self, level):
        try:
            wmi_obj = wmi.WMI(namespace='wmi')
            methods = wmi_obj.WmiMonitorBrightnessMethods()[0]
            level_to_set = min(100, max(0, int(level)))
            methods.WmiSetBrightness(level_to_set, 0)
            self.bot_response(f"Brightness set to {level_to_set} percent.")
        except Exception:
            self.bot_response("Sorry, I was unable to set the brightness.")
    
    def brightness_up(self):
        try:
            wmi_obj = wmi.WMI(namespace='wmi')
            curr = wmi_obj.WmiMonitorBrightness()[0].CurrentBrightness
            new = min(100, curr + 10)
            wmi_obj.WmiMonitorBrightnessMethods()[0].WmiSetBrightness(int(new), 0)
            self.bot_response(f"Brightness increased to {new} percent.")
        except Exception:
            try:
                pyautogui.press('brightnessup')
                self.bot_response("Brightness up.")
            except Exception:
                self.bot_response("Couldn't increase brightness.")
    
    def brightness_down(self):
        try:
            wmi_obj = wmi.WMI(namespace='wmi')
            curr = wmi_obj.WmiMonitorBrightness()[0].CurrentBrightness
            new = max(0, curr - 10)
            wmi_obj.WmiMonitorBrightnessMethods()[0].WmiSetBrightness(int(new), 0)
            self.bot_response(f"Brightness decreased to {new} percent.")
        except Exception:
            try:
                pyautogui.press('brightnessdown')
                self.bot_response("Brightness down.")
            except Exception:
                self.bot_response("Couldn't decrease brightness.")
    
    def open_app(self, query):
        app_name = query.replace("open", "").strip()
        app_paths = {
            "notepad": "notepad.exe",
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "calculator": "calc.exe",
            "vscode": "C:\\Users\\HP\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
        }
        if app_name in app_paths:
            try:
                os.startfile(app_paths[app_name])
                self.bot_response(f"Opening {app_name}.")
            except FileNotFoundError:
                self.bot_response(f"The path for {app_name} was not found.")
        else:
            self.bot_response(f"Sorry, I don't know the path for {app_name}.")
    
    def open_folder(self, query):
        query = query.lower()
        user = os.path.expanduser("~")
        folders = {
            "desktop": os.path.join(user, "Desktop"),
            "downloads": os.path.join(user, "Downloads"),
            "documents": os.path.join(user, "Documents"),
            "pictures": os.path.join(user, "Pictures"),
            "videos": os.path.join(user, "Videos"),
            "music": os.path.join(user, "Music"),
            "c drive": "C:\\",
            "d drive": "D:\\",
            "e drive": "E:\\"
        }
        onedrive = os.path.join(user, "OneDrive")
        if os.path.exists(onedrive):
            for key in ["downloads", "documents", "pictures", "desktop"]:
                possible = os.path.join(onedrive, key.capitalize())
                if os.path.exists(possible):
                    folders[key] = possible
        for name, path in folders.items():
            if name.replace(" ", "") in query.replace(" ", ""):
                if os.path.exists(path):
                    try:
                        os.startfile(path)
                        self.bot_response(f"Opening your {name} folder.")
                    except:
                        webbrowser.open(path)
                        self.bot_response(f"Opening your {name} folder.")
                else:
                    self.bot_response(f"Sorry, I couldn't find your {name} folder.")
                return
        self.bot_response("Please specify a valid folder to open.")
    
    def empty_recycle_bin(self):
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
            self.bot_response("Recycle bin is emptied.")
        except Exception:
            self.bot_response("The recycle bin is already empty.")
    
    def wish_me(self):
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            self.bot_response("Good Morning!")
        elif 12 <= hour < 18:
            self.bot_response("Good Afternoon!")
        else:
            self.bot_response("Good Evening!")
    
    # ========== MAIN COMMAND PROCESSOR ==========
    
    def process_command(self, query):
        """Process all commands"""
        self.update_status("PROCESSING", '#00d4ff')
        
        try:
            # Browser Commands
            if "new tab" in query:
                pyautogui.hotkey('ctrl', 't')
                self.bot_response("New tab.")
            elif "close tab" in query:
                pyautogui.hotkey('ctrl', 'w')
                self.bot_response("Closing tab.")
            elif "reopen tab" in query:
                pyautogui.hotkey('ctrl', 'shift', 't')
                self.bot_response("Reopening tab.")
            elif "next tab" in query:
                pyautogui.hotkey('ctrl', 'tab')
                self.bot_response("Next tab.")
            elif any(term in query for term in ["previous tab", "last tab"]):
                pyautogui.hotkey('ctrl', 'shift', 'tab')
                self.bot_response("Previous tab.")
            elif "new window" in query:
                pyautogui.hotkey('ctrl', 'n')
                self.bot_response("New window.")
            elif "incognito" in query:
                pyautogui.hotkey('ctrl', 'shift', 'n')
                self.bot_response("Incognito window.")
            elif "refresh" in query:
                pyautogui.hotkey('f5')
                self.bot_response("Refreshing.")
            elif "go back" in query:
                pyautogui.hotkey('alt', 'left')
                self.bot_response("Going back.")
            elif "go forward" in query:
                pyautogui.hotkey('alt', 'right')
                self.bot_response("Going forward.")
            elif "scroll up" in query:
                pyautogui.scroll(2000)
                self.bot_response("Scrolling up.")
            elif "scroll down" in query:
                pyautogui.scroll(-2000)
                self.bot_response("Scrolling down.")
            
            # Volume Control
            elif "volume" in query and not any(k in query for k in ["up", "down", "increase", "decrease", "mute", "unmute", "raise", "lower"]):
                level = self.extract_number(query)
                if level is not None:
                    self.set_system_volume(level)
                else:
                    self.bot_response("Please tell me the volume level to set.")
            elif any(term in query for term in ["set volume to", "change volume to", "set volume", "change volume"]):
                level = self.extract_number(query)
                if level is not None:
                    self.set_system_volume(level)
                else:
                    self.bot_response("Please tell me a number to set the volume to.")
            elif any(term in query for term in ["volume up", "increase volume", "raise volume"]):
                pyautogui.press('volumeup')
                self.bot_response("Volume up.")
            elif any(term in query for term in ["volume down", "decrease volume", "lower volume"]):
                pyautogui.press('volumedown')
                self.bot_response("Volume down.")
            elif any(term in query for term in ["mute", "mute audio", "silence"]):
                pyautogui.press('volumemute')
                self.bot_response("Muted.")
            elif "unmute" in query:
                pyautogui.press('volumeunmute')
                self.bot_response("Unmuted.")
            
            # Brightness Control
            elif "brightness" in query and not any(k in query for k in ["up", "down", "increase", "decrease", "raise", "lower"]):
                level = self.extract_number(query)
                if level is not None:
                    self.set_brightness(level)
                else:
                    self.bot_response("Please tell me the brightness level to set.")
            elif any(term in query for term in ["set brightness to", "change brightness to", "set brightness", "change brightness"]):
                level = self.extract_number(query)
                if level is not None:
                    self.set_brightness(level)
                else:
                    self.bot_response("Please tell me a number to set the brightness to.")
            elif any(term in query for term in ["brightness up", "increase brightness", "raise brightness"]):
                self.brightness_up()
            elif any(term in query for term in ["brightness down", "decrease brightness", "lower brightness"]):
                self.brightness_down()
            
            # Calculator
            elif ("calculate" in query or
                  "plus" in query or
                  "minus" in query or
                  "add" in query or
                  "subtract" in query or
                  "multiply" in query or
                  "divide" in query or
                  "square" in query or
                  "cube" in query or
                  "power" in query or
                  "root" in query or
                  "percent" in query):
                self.calculate(query)
            
            # Window Management
            elif any(term in query for term in ["minimize", "minimize this"]):
                pyautogui.hotkey('win', 'down')
                self.bot_response("Minimized.")
            elif "maximize" in query:
                pyautogui.hotkey('win', 'up')
                self.bot_response("Maximized.")
            elif "restore window" in query:
                pyautogui.hotkey('win', 'shift', 'm')
                self.bot_response("Restored window.")
            elif any(term in query for term in ["switch window", "change window", "swap window", "next window", "other window"]):
                pyautogui.hotkey('alt', 'tab')
                self.bot_response("Window switched.")
            elif any(term in query for term in ["show desktop", "show my desktop", "hide all windows"]):
                pyautogui.hotkey('win', 'd')
                self.bot_response("Showing desktop.")
            elif "open settings" in query:
                pyautogui.hotkey('win', 'i')
                self.bot_response("Opening Settings.")
            elif any(term in query for term in ["close window", "close this", "close the window"]):
                pyautogui.hotkey('alt', 'f4')
                self.bot_response("Closing window.")
            elif any(term in query for term in ["lock my computer", "lock windows"]):
                ctypes.windll.user32.LockWorkStation()
                self.bot_response("Locked computer.")
            elif any(term in query for term in ["shutdown", "shut down the computer", "turn off"]):
                self.bot_response("Shutting down.")
                os.system("shutdown /s /t 1")
            elif any(term in query for term in ["restart", "reboot"]):
                self.bot_response("Restarting.")
                os.system("shutdown /r /t 1")
            elif "sleep" in query:
                self.bot_response("Sleeping.")
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif "hibernate" in query:
                self.bot_response("Hibernating.")
                os.system("shutdown /h")
            elif "open control panel" in query:
                os.system("control")
                self.bot_response("Opening Control Panel.")
            elif "task manager" in query:
                os.system("Taskmgr")
                self.bot_response("Opening Task Manager.")
            
            # File Operations
            elif "open" in query and (
                    "folder" in query or
                    "desktop" in query or
                    "downloads" in query or
                    "documents" in query or
                    "pictures" in query or
                    "videos" in query or
                    "music" in query or
                    "drive" in query):
                self.open_folder(query)
            
            elif "open" in query:
                if any(site in query for site in ["website", "google", "youtube", "facebook", "instagram", "twitter", "linkedin", "github", "gmail"]):
                    self.open_website(query)
                elif any(app in query for app in ["notepad", "chrome", "calculator", "vscode"]):
                    self.open_app(query)
                else:
                    self.bot_response("I can't open that. Please specify a website, app, or folder.")
            
            # Search
            elif any(term in query for term in ["search", "look up", "find"]):
                if "google" in query:
                    self.search_google(query)
                elif "wikipedia" in query:
                    self.search_wikipedia(query)
                else:
                    self.search_google(query)
            
            # Media
            elif "play" in query:
                self.play_song(query)
            
            # Information
            elif any(term in query for term in ["time", "what time is it"]):
                self.tell_time()
            elif any(term in query for term in ["date", "what day is it", "what is the date", "data"]):
                self.tell_date()
            elif any(term in query for term in ["hello", "hi", "hey"]):
                self.bot_response("Hello there. How can I help you?")
            elif "wish me" in query or "greet me" in query:
                self.wish_me()
            elif any(term in query for term in ["joke", "tell me a joke"]):
                self.bot_response(pyjokes.get_joke())
            elif "news" in query:
                self.get_news()
            elif "weather" in query:
                self.get_weather(query)
            elif any(term in query for term in ["system stats", "system status", "status"]):
                self.system_status()
            elif "screenshot" in query:
                self.take_screenshot()
            
            # Notes & Tasks
            elif any(term in query for term in ["add a task", "add task", "atask"]):
                self.todo_add(query)
            elif any(term in query for term in ["show tasks", "to do show", "tudu show", "what are my tasks"]):
                self.todo_show()
            elif any(term in query for term in ["remember this", "make a note", "note down"]):
                self.remember_note(query)
            elif any(term in query for term in ["recall notes", "show notes", "what did i remember"]):
                self.recall_notes()
            elif any(term in query for term in ["clear notes", "delete my notes"]):
                self.clear_notes()
            
            # System
            elif any(term in query for term in ["empty recycle bin", "clean recycle bin", "clear recycle bin"]):
                self.empty_recycle_bin()
            
            # Exit
            elif any(term in query for term in ["exit", "quit", "bye", "goodbye", "kill yourself", "kill", "die"]):
                self.bot_response("Goodbye, have a great day.")
                self.continuous_mode = False
                self.root.after(2000, self.root.destroy)
            
            else:
                self.bot_response("Sorry, I didn't catch that.")
        
        except Exception as e:
            print(f"Error: {e}")
            self.bot_response("Sorry, there was an error processing your command.")
        
        finally:
            if not self.continuous_mode:
                self.update_status("STANDBY", '#00d4ff')
                self.set_visual_state('idle')

def main():
    root = tk.Tk()
    app = VetoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
