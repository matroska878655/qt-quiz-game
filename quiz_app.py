"""
Quiz Master Pro - Modern Edition with CustomTkinter
A fun quiz application with multiple categories and a modern, smooth GUI
With full Arabic RTL support
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import random
import time
from datetime import datetime
import os
import re

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

# Try to import Arabic text processing libraries
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    print("Arabic support libraries not found. Installing...")
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "arabic-reshaper", "python-bidi"])
        import arabic_reshaper
        from bidi.algorithm import get_display
        ARABIC_SUPPORT = True
        print("Arabic support libraries installed successfully.")
    except:
        print("Failed to install Arabic support libraries. Arabic text may not display correctly.")

class ModernQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Master Pro")
        self.root.geometry("1000x700")  # Increased size to prevent content cutoff
        
        # Configure grid weights for responsive layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Track the current question bank file
        self.current_question_file = None
        
        # Initialize with a default question bank
        self.create_default_question_bank()
        
        # Game state variables
        self.current_cat = None
        self.quiz_questions = []
        self.q_number = 0
        self.player_score = 0
        self.wrong_answers = 0  # Track wrong answers separately
        self.time_remaining = 30
        self.timer_active = False
        self.chosen_option = None
        self.game_in_progress = False
        self.answer_locked = False  # Prevent multiple clicks
        
        # Wait a bit before showing file dialog
        self.root.after(100, self.select_question_file)
        
    def process_text(self, text):
        """Process text for proper display, handling Arabic RTL"""
        # Check if text contains Arabic characters using regex directly
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        if arabic_pattern.search(text) and ARABIC_SUPPORT:
            # Reshape Arabic text for proper display
            reshaped_text = arabic_reshaper.reshape(text)
            # Apply bidirectional algorithm for correct display
            bidi_text = get_display(reshaped_text)
            return bidi_text
        return text
        
    def create_default_question_bank(self):
        """Create a simple default question bank in current directory"""
        # NOTE: This is a fallback in case no file is selected
        # TODO: Make this more robust with more categories
        default_questions = {
            "تشريح عصبي": [
                {
                    "question": "اين مركز تنظيم التنفس وضربات القلب في الدماغ؟",
                    "options": ["القشرة الدماغية", "النخاع المستطيل", "المخيخ", "الجسر"],
                    "answer": 1
                },
                {
                    "question": "أكبر جزء في الدماغ؟",
                    "options": ["المخ", "المخيخ", "الجذع الدماغي", "البصلة السيسائية"],
                    "answer": 0
                },
                {
                    "question": "المادة البيضاء في الدماغ هي؟",
                    "options": ["أجسام الخلايا العصبية", "محاوبر الخلايا العصبية", "المشابك العصبية", "النهايات العصبية"],
                    "answer": 1
                }
            ]
        }
        
        # Save to a file in the current directory
        file_path = os.path.join(os.getcwd(), "default_questions.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_questions, f, indent=2, ensure_ascii=False)
            
        self.current_question_file = file_path
        self.questions_db = default_questions
        
    def select_question_file(self):
        """Open file dialog to select a question bank JSON file"""
        # If no file selected yet, prompt for one
        if not self.current_question_file:
            file_path = filedialog.askopenfilename(
                title="Select Question Bank File",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            
            if not file_path:  # User cancelled
                # Keep using default
                self.show_main_screen()
                return
                
            self.current_question_file = file_path
            self.load_questions_from_file(file_path)
        else:
            self.show_main_screen()
            
    def load_questions_from_file(self, file_path):
        """Load questions from the specified file path"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.questions_db = json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to load questions from {file_path}:\n{str(e)}")
            return False
    
    def reload_questions(self):
        """Reload questions from the current file"""
        if self.current_question_file:
            if self.load_questions_from_file(self.current_question_file):
                messagebox.showinfo("Success", "Questions reloaded successfully!")
                self.show_main_screen()
        else:
            messagebox.showerror("Error", "Failed to reload questions!")
        
    def show_main_screen(self):
        """Display the main menu with category selection"""
        # Clear everything first
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container with proper grid layout
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Title section
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        main_title = ctk.CTkLabel(
            title_frame,
            text="🎯 Quiz Master Pro",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        main_title.pack(pady=10)
        
        tagline = ctk.CTkLabel(
            title_frame,
            text="Challenge yourself with questions from different topics!",
            font=ctk.CTkFont(size=16)
        )
        tagline.pack()
        
        # Current question bank info
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Display current question file
        file_display = os.path.basename(self.current_question_file) if self.current_question_file else "No file selected"
        ctk.CTkLabel(
            info_frame,
            text=f"Current Question Bank: {file_display}",
            font=ctk.CTkFont(size=14),
            text_color=("#F59E0B" if self.current_question_file else "#EF4444")
        ).pack(pady=10)
        
        # Category selection frame
        cat_frame = ctk.CTkFrame(main_frame)
        cat_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        cat_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            cat_frame,
            text="Pick a Category:",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Category buttons container
        cat_buttons = ctk.CTkFrame(cat_frame, fg_color="transparent")
        cat_buttons.pack(pady=10)
        
        if self.questions_db:
            categories = list(self.questions_db.keys())
            for idx, category in enumerate(categories):
                # Process category text for Arabic support
                display_category = self.process_text(category)
                # Check if category contains Arabic for RTL alignment
                arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
                is_arabic_cat = bool(arabic_pattern.search(category))
                
                btn = ctk.CTkButton(
                    cat_buttons,
                    text=display_category,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    width=200,
                    height=50,
                    command=lambda cat=category: self.begin_quiz(cat)
                )
                # Configure RTL for Arabic categories
                if is_arabic_cat:
                    btn.configure(anchor="e")
                btn.grid(row=idx//2, column=idx%2, padx=15, pady=15)
        else:
            ctk.CTkLabel(
                cat_frame,
                text="No categories found in the question bank!",
                font=ctk.CTkFont(size=16),
                text_color="#EF4444"
            ).pack(pady=20)
        
        # Options buttons frame
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        
        # High scores button
        highscores_btn = ctk.CTkButton(
            options_frame,
            text="🏆 View High Scores",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            command=self.display_highscores
        )
        highscores_btn.pack(side="left", padx=10)
        
        # Reload questions button
        reload_btn = ctk.CTkButton(
            options_frame,
            text="🔄 Reload Questions",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            command=self.reload_questions
        )
        reload_btn.pack(side="left", padx=10)
        
        # Change question bank button
        change_btn = ctk.CTkButton(
            options_frame,
            text="📁 Change Question Bank",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            command=self.change_question_bank
        )
        change_btn.pack(side="left", padx=10)
        
    def change_question_bank(self):
        """Allow user to select a different question bank file"""
        file_path = filedialog.askopenfilename(
            title="Select Question Bank File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.current_question_file = file_path
            if self.load_questions_from_file(file_path):
                messagebox.showinfo("Success", "Question bank loaded successfully!")
                self.show_main_screen()
        
    def begin_quiz(self, category):
        """Start a new quiz with the selected category"""
        self.current_cat = category
        # Shuffle questions so it's different each time
        self.quiz_questions = random.sample(self.questions_db[category], len(self.questions_db[category]))
        self.q_number = 0
        self.player_score = 0
        self.wrong_answers = 0  # Reset wrong answers
        self.game_in_progress = True
        self.answer_locked = False
        self.display_question()
        
    def display_question(self):
        """Show the current question with modern UI"""
        # Clear the screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container with proper grid layout
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Check if quiz is over
        if self.q_number >= len(self.quiz_questions):
            self.show_final_results()
            return
            
        current_q = self.quiz_questions[self.q_number]
        self.answer_locked = False  # Reset for new question
        self.chosen_option = None  # Reset chosen option
        
        # Check if this is an Arabic quiz using inline check
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        is_arabic_quiz = bool(arabic_pattern.search(current_q['question']))
        
        # Top bar with category and score
        top_bar = ctk.CTkFrame(main_frame)
        top_bar.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        top_bar.grid_columnconfigure(1, weight=1)
        
        # Category label - Process for Arabic support
        display_category = self.process_text(f"Topic: {self.current_cat}")
        cat_label = ctk.CTkLabel(
            top_bar,
            text=display_category,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        cat_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Score display - Format: correct(green) - wrong(red)
        score_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        score_frame.grid(row=0, column=1, padx=20, pady=10, sticky="e")
        
        # Correct score in green
        self.correct_label = ctk.CTkLabel(
            score_frame,
            text=str(self.player_score),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#10B981"
        )
        self.correct_label.pack(side="left")
        
        # Separator
        separator_label = ctk.CTkLabel(
            score_frame,
            text=" - ",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        separator_label.pack(side="left")
        
        # Wrong score in red
        self.wrong_label = ctk.CTkLabel(
            score_frame,
            text=str(self.wrong_answers),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#EF4444"
        )
        self.wrong_label.pack(side="left")
        
        # Progress bar
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        progress_bar = ctk.CTkProgressBar(
            progress_frame,
            progress_color=("#3B82F6", "#1D4ED8"),
            width=400
        )
        progress_bar.pack(pady=10)
        progress_bar.set(self.q_number / len(self.quiz_questions))
        
        # Question counter
        counter_text = f"Question {self.q_number + 1} of {len(self.quiz_questions)}"
        # if is_arabic_quiz:
        #     counter_text = f"السؤال {self.q_number + 1} من {len(self.quiz_questions)}"
        ctk.CTkLabel(
            progress_frame,
            text=counter_text,
            font=ctk.CTkFont(size=14)
        ).pack(pady=5)
        
        # Timer display
        timer_text = f"Time: {self.time_remaining}s"
        # if is_arabic_quiz:
        #     timer_text = f"الوقت: {self.time_remaining} ثانية"
        self.timer_display = ctk.CTkLabel(
            progress_frame,
            text=timer_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#F59E0B" if self.time_remaining > 10 else "#EF4444")
        )
        self.timer_display.pack(pady=5)
        
        # Question card with proper sizing
        q_card = ctk.CTkFrame(main_frame)
        q_card.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        q_card.grid_columnconfigure(0, weight=1)
        
        # Process question text for Arabic support
        question_text = self.process_text(current_q['question'])
        question_label = ctk.CTkLabel(
            q_card,
            text=question_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            wraplength=800,  # Ensure text wraps properly
            justify="right" if is_arabic_quiz else "center"
        )
        question_label.grid(row=0, column=0, padx=30, pady=30, sticky="ew")
        
        # Answer options frame
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        options_frame.grid_columnconfigure(0, weight=1)
        
        self.option_buttons = []
        for i, option in enumerate(current_q['options']):
            # Process option text for Arabic support
            display_option = self.process_text(option)
            # Create option button with proper styling
            opt_btn = ctk.CTkButton(
                options_frame,
                text=display_option,
                font=ctk.CTkFont(size=16),
                height=50,
                command=lambda idx=i: self.on_answer_click(idx),
                anchor="e" if is_arabic_quiz else "center"
            )
            opt_btn.grid(row=i, column=0, padx=20, pady=10, sticky="ew")
            
            # Store the index with the button
            opt_btn.answer_index = i
            self.option_buttons.append(opt_btn)
        
        # Start the countdown timer
        self.time_remaining = 30
        self.timer_active = True
        self.run_timer()
        
    def update_score_display(self):
        """Update the score display with correct(green) - wrong(red) format"""
        # Simply update the text of the existing labels
        self.correct_label.configure(text=str(self.player_score))
        self.wrong_label.configure(text=str(self.wrong_answers))
        
    def on_answer_click(self, index):
        """
        Handle when user clicks an answer.
        This function:
        1. Locks the answer to prevent multiple clicks
        2. Shows the result (correct/incorrect)
        3. Updates the score
        4. Automatically moves to the next question after a delay
        """
        if self.answer_locked:
            return  # Prevent multiple clicks
            
        self.answer_locked = True
        self.timer_active = False  # Stop the timer
        
        print(f"Answer clicked: {index}")  # Debug
        
        # Highlight selected answer
        self.chosen_option = index
        
        current_q = self.quiz_questions[self.q_number]
        
        # Check if correct and update score
        is_correct = (self.chosen_option == current_q['answer'])
        
        if is_correct:
            # Correct answer!
            self.option_buttons[index].configure(fg_color=("#10B981", "#059669"))
            self.player_score += 1
            print(f"Correct! Score: {self.player_score}")  # Debug
        else:
            # Wrong answer - show selected in red and correct in green
            self.option_buttons[index].configure(fg_color=("#EF4444", "#DC2626"))
            self.option_buttons[current_q['answer']].configure(fg_color=("#10B981", "#059669"))
            self.wrong_answers += 1  # Increment wrong answers
            print(f"Wrong! Score: {self.player_score}")  # Debug
        
        # Disable all options
        for btn in self.option_buttons:
            btn.configure(state="disabled")
        
        # Update score display immediately
        self.update_score_display()
        
        # Wait 1.5 seconds then go to the next question
        self.root.after(1500, self.auto_next_question)
        
    def auto_next_question(self):
        """Automatically move to the next question"""
        print(f"Auto-moving to the next question. Current: {self.q_number}")  # Debug
        self.q_number += 1
        self.display_question()
        
    def run_timer(self):
        """Countdown timer for each question"""
        if self.timer_active and self.time_remaining > 0:
            self.time_remaining -= 1
            
            # Update timer text based on language
            current_q = self.quiz_questions[self.q_number]
            # Check if this is an Arabic quiz using inline check
            arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
            is_arabic_quiz = bool(arabic_pattern.search(current_q['question']))
            
            timer_text = f"Time: {self.time_remaining}s"
            # if is_arabic_quiz:
            #     timer_text = f"الوقت: {self.time_remaining} ثانية"
                
            self.timer_display.configure(text=timer_text)
            
            # Make it red when time is running out
            if self.time_remaining <= 10:
                self.timer_display.configure(text_color="#EF4444")
            
            # Continue counting
            self.root.after(1000, self.run_timer)
        elif self.timer_active:
            # Time's up - treat as no answer
            self.answer_locked = True
            current_q = self.quiz_questions[self.q_number]
            
            # Show the correct answer
            self.option_buttons[current_q['answer']].configure(fg_color=("#10B981", "#059669"))
            
            # Add to score history as wrong
            self.wrong_answers += 1
            
            # Disable all options
            for btn in self.option_buttons:
                btn.configure(state="disabled")
            
            # Update score display
            self.update_score_display()
            
            # Wait 1.5 seconds then go to the next question
            self.root.after(1500, self.auto_next_question)
            
    def show_final_results(self):
        """Display the final score and results"""
        # Clear the screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Check if this was an Arabic quiz using inline check
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        is_arabic_quiz = bool(arabic_pattern.search(self.current_cat))
        
        # Main container with proper grid layout
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Results card
        results_card = ctk.CTkFrame(main_frame)
        results_card.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        results_card.grid_columnconfigure(0, weight=1)
        
        # Big trophy!
        ctk.CTkLabel(
            results_card,
            text="🏆",
            font=ctk.CTkFont(size=72)
        ).grid(row=0, column=0, pady=20)
        
        # Results title
        title_text = "Quiz Complete!"
        if is_arabic_quiz:
            title_text = "انتهى الاختبار!"
        ctk.CTkLabel(
            results_card,
            text=self.process_text(title_text),
            font=ctk.CTkFont(size=32, weight="bold")
        ).grid(row=1, column=0, pady=10)
        
        # Calculate percentage
        total_qs = len(self.quiz_questions)
        percent = (self.player_score / total_qs) * 100
        
        # Score display with the same format as during quiz
        score_frame = ctk.CTkFrame(results_card, fg_color="transparent")
        score_frame.grid(row=2, column=0, pady=10)
        
        # Correct score in green
        correct_label = ctk.CTkLabel(
            score_frame,
            text=str(self.player_score),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#10B981"
        )
        correct_label.pack(side="left")
        
        # Separator
        separator_label = ctk.CTkLabel(
            score_frame,
            text=" - ",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        separator_label.pack(side="left")
        
        # Wrong score in red
        wrong_label = ctk.CTkLabel(
            score_frame,
            text=str(self.wrong_answers),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#EF4444"
        )
        wrong_label.pack(side="left")
        
        # Percentage
        percent_text = f"{percent:.1f}%"
        ctk.CTkLabel(
            results_card,
            text=percent_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#10B981" if percent >= 60 else "#F59E0B")
        ).grid(row=3, column=0, pady=5)
        
        # Motivational message based on performance
        if percent >= 80:
            msg = "Amazing! You're a quiz champion! 🌟"
            msg_color = "#10B981"
        elif percent >= 60:
            msg = "Good work! Keep it up! 👍"
            msg_color = "#F59E0B"
        else:
            msg = "Nice try! Practice makes perfect! 💪"
            msg_color = "#EF4444"
            
        ctk.CTkLabel(
            results_card,
            text=self.process_text(msg),
            font=ctk.CTkFont(size=16),
            text_color=msg_color
        ).grid(row=4, column=0, pady=20)
        
        # Action buttons
        button_row = ctk.CTkFrame(results_card, fg_color="transparent")
        button_row.grid(row=5, column=0, pady=30)
        
        # Play again button
        play_text = "Play Again" if not is_arabic_quiz else "العب مرة أخرى"
        again_btn = ctk.CTkButton(
            button_row,
            text=self.process_text(play_text),
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            command=lambda: self.begin_quiz(self.current_cat)
        )
        again_btn.pack(side="left", padx=10)
        
        # Main menu button
        menu_text = "Main Menu" if not is_arabic_quiz else "القائمة الرئيسية"
        menu_btn = ctk.CTkButton(
            button_row,
            text=self.process_text(menu_text),
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            command=self.show_main_screen
        )
        menu_btn.pack(side="left", padx=10)
        
        # Save this score
        self.save_score(self.player_score, self.current_cat)
        
    def save_score(self, score, category):
        """Save high scores to a JSON file"""
        try:
            # Try to load existing scores
            with open('quiz_scores.json', 'r', encoding='utf-8') as f:
                saved_scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create new if doesn't exist
            saved_scores = {}
            
        # Add score for this category
        if category not in saved_scores:
            saved_scores[category] = []
            
        saved_scores[category].append({
            'score': score,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        
        # Keep only top 5 scores
        saved_scores[category] = sorted(saved_scores[category], 
                                       key=lambda x: x['score'], 
                                       reverse=True)[:5]
        
        # Save back to file
        with open('quiz_scores.json', 'w', encoding='utf-8') as f:
            json.dump(saved_scores, f, indent=2, ensure_ascii=False)
            
    def display_highscores(self):
        """Show the high scores screen"""
        # Clear the screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container with proper grid layout
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="🏆 Hall of Fame",
            font=ctk.CTkFont(size=32, weight="bold")
        ).grid(row=0, column=0, pady=20)
        
        # Scores card with scrollable frame
        scores_card = ctk.CTkScrollableFrame(main_frame, height=400)
        scores_card.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        scores_card.grid_columnconfigure(0, weight=1)
        
        # Load scores
        try:
            with open('quiz_scores.json', 'r', encoding='utf-8') as f:
                scores_data = json.load(f)
        except:
            scores_data = {}
        
        if not scores_data:
            ctk.CTkLabel(
                scores_card,
                text="No scores recorded yet!",
                font=ctk.CTkFont(size=16)
            ).pack(pady=20)
        else:
            # Show scores for each category
            for cat, cat_scores in scores_data.items():
                # Category header - Process for Arabic support
                display_category = self.process_text(cat)
                # Check if category contains Arabic for RTL alignment
                arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
                is_arabic_cat = bool(arabic_pattern.search(cat))
                
                cat_label = ctk.CTkLabel(
                    scores_card,
                    text=display_category,
                    font=ctk.CTkFont(size=18, weight="bold"),
                    anchor="e" if is_arabic_cat else "center"
                )
                cat_label.pack(pady=(20, 10))
                
                # List scores
                for rank, score_info in enumerate(cat_scores, 1):
                    max_possible = len(self.questions_db.get(cat, []))
                    score_line = f"{rank}. {score_info['score']}/{max_possible} - {score_info['date']}"
                    if is_arabic_cat:
                        score_line = f"{rank}. {score_info['score']}/{max_possible} - {score_info['date']}"
                    ctk.CTkLabel(
                        scores_card,
                        text=score_line,
                        font=ctk.CTkFont(size=14),
                        anchor="e" if is_arabic_cat else "center"
                    ).pack(pady=2)
        
        # Back button
        back_btn = ctk.CTkButton(
            main_frame,
            text="← Back to Menu",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            command=self.show_main_screen
        )
        back_btn.grid(row=2, column=0, pady=20)

# Main execution
if __name__ == "__main__":
    # Create and run the app
    root = ctk.CTk()
    app = ModernQuizApp(root)
    
    # Start the main loop
    root.mainloop()