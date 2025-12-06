# quiz_gui_with_images.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import random
import os
import sys

# Pillow for image loading/resizing
try:
    from PIL import Image, ImageTk
except Exception:
    raise RuntimeError("Pillow is required. Install with: pip install pillow")

APP_TITLE = "Quiz GUI (with images)"

def read_csv_questions(path):
    """
    Expects columns:
      - Question Type
      - Question Title
      - Choices            (comma-separated texts)
      - Correct Answer(s)  (comma-separated texts, matching choice text)
      - Image Full Path    (optional, full path to image file; empty if none)
    """
    df = pd.read_csv(path, encoding="utf-8", sep=",")
    questions = []
    for _, row in df.iterrows():
        q = {
            "type": str(row.get("Question Type", "")).strip(),
            "title": str(row.get("Question Title", "")).strip(),
            "choices": [c.strip() for c in str(row.get("Choices", "")).split(",") if c.strip() != ""],
            "correct": [c.strip() for c in str(row.get("Correct Answer(s)", "")).split(",") if c.strip() != ""],
            "image": str(row.get("Image Full Path", "")).strip() if "Image Full Path" in row.index else ""
        }
        # Normalize empty image string to empty
        if q["image"].lower() in ("nan", "none"):
            q["image"] = ""
        questions.append(q)
    return questions

def shuffle_quiz_copy(questions):
    qs = []
    for q in questions:
        copy_q = {
            "type": q["type"],
            "title": q["title"],
            "choices": q["choices"][:],  # copy list
            "correct": q["correct"][:],
            "image": q.get("image", "")
        }
        random.shuffle(copy_q["choices"])
        qs.append(copy_q)
    random.shuffle(qs)
    return qs

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("880x640")
        self.minsize(640, 420)

        self.questions_original = []
        self.questions = []
        self.index = 0
        self.score = 0
        self.answered_count = 0

        # Keep a reference to PhotoImage to avoid being GC'd
        self._photo_image_ref = None

        self.create_widgets()
        self.update_controls_state(enabled=False)

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=8)

        btn_open = ttk.Button(top, text="Open CSV", command=self.open_file)
        btn_open.pack(side="left")

        self.shuffle_var = tk.BooleanVar(value=False)
        chk_shuffle = ttk.Checkbutton(top, text="Shuffle questions & choices", variable=self.shuffle_var)
        chk_shuffle.pack(side="left", padx=8)

        btn_restart = ttk.Button(top, text="Restart", command=self.restart_quiz)
        btn_restart.pack(side="left", padx=8)

        btn_quit = ttk.Button(top, text="Quit", command=self.on_quit)
        btn_quit.pack(side="right")

        center = ttk.Frame(self)
        center.pack(fill="both", expand=True, padx=8, pady=4)

        header_frame = ttk.Frame(center)
        header_frame.pack(fill="x")
        self.lbl_progress = ttk.Label(header_frame, text="No file loaded", anchor="w")
        self.lbl_progress.pack(side="left")
        self.lbl_score = ttk.Label(header_frame, text="Score: 0", anchor="e")
        self.lbl_score.pack(side="right")

        self.lbl_qtype = ttk.Label(center, text="", font=("Segoe UI", 10, "italic"))
        self.lbl_qtype.pack(anchor="w", pady=(8,0))

        self.txt_title = tk.Text(center, height=3, wrap="word", font=("Segoe UI", 12))
        self.txt_title.configure(state="disabled", background=self.cget("bg"), relief="flat")
        self.txt_title.pack(fill="x", pady=(4,8))

        # Image canvas/label (hidden if no image)
        self.image_frame = ttk.Frame(center)
        self.image_frame.pack(fill="both", expand=False)
        self.lbl_image = ttk.Label(self.image_frame)
        self.lbl_image.pack(padx=4, pady=4)

        # Choices frame
        self.frame_choices = ttk.Frame(center)
        self.frame_choices.pack(fill="both", expand=True)

        self.lbl_feedback = ttk.Label(center, text="", font=("Segoe UI", 10))
        self.lbl_feedback.pack(pady=(4,4))

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=8, pady=8)
        self.btn_submit = ttk.Button(bottom, text="Submit Answer", command=self.submit_answer)
        self.btn_submit.pack(side="left")
        self.btn_next = ttk.Button(bottom, text="Next", command=self.next_question)
        self.btn_next.pack(side="left", padx=8)
        self.btn_prev = ttk.Button(bottom, text="Previous", command=self.prev_question)
        self.btn_prev.pack(side="left", padx=8)

        self.progress = ttk.Progressbar(bottom, mode="determinate")
        self.progress.pack(side="right", fill="x", expand=True)

        self.choice_vars = []
        self.choice_widgets = []

    def open_file(self):
        path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files","*.csv"), ("All files","*.*")])
        if not path:
            return
        try:
            self.questions_original = read_csv_questions(path)
            if len(self.questions_original) == 0:
                messagebox.showwarning(APP_TITLE, "No questions found in file.")
                return
            if self.shuffle_var.get():
                self.questions = shuffle_quiz_copy(self.questions_original)
            else:
                self.questions = [ {"type":q["type"], "title":q["title"], "choices": q["choices"][:], "correct": q["correct"][:], "image": q.get("image","")} for q in self.questions_original ]
            self.index = 0
            self.score = 0
            self.answered_count = 0
            self.update_controls_state(enabled=True)
            self.show_question()
            self.center_window()
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Failed to read file:\n{e}")

    def restart_quiz(self):
        if not self.questions_original:
            return
        if self.shuffle_var.get():
            self.questions = shuffle_quiz_copy(self.questions_original)
        else:
            self.questions = [ {"type":q["type"], "title":q["title"], "choices": q["choices"][:], "correct": q["correct"][:], "image": q.get("image","")} for q in self.questions_original ]
        self.index = 0
        self.score = 0
        self.answered_count = 0
        self.lbl_feedback.config(text="")
        self._photo_image_ref = None
        self.show_question()

    def update_controls_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for w in (self.btn_submit, self.btn_next, self.btn_prev):
            try:
                w.config(state=state)
            except Exception:
                pass
        self.progress['value'] = 0
        self.lbl_score.config(text=f"Score: {self.score}")

    def show_question(self):
        q = self.questions[self.index]
        self.lbl_qtype.config(text=f"{q['type']}")
        self.txt_title.configure(state="normal")
        self.txt_title.delete("1.0", "end")
        self.txt_title.insert("1.0", q['title'])
        self.txt_title.configure(state="disabled")

        # Image handling: show if path provided and file exists
        self._photo_image_ref = None
        img_path = q.get("image", "")
        if img_path:
            # Expand user and relative paths
            img_path = os.path.expanduser(img_path)
            if not os.path.isabs(img_path):
                # If the path is relative, make it relative to the CSV file location if possible
                # We don't have the CSV path here; users should provide absolute paths ideally.
                img_path = os.path.abspath(img_path)

        if img_path and os.path.exists(img_path) and os.path.isfile(img_path):
            try:
                # Load image and scale to fit max dimensions
                max_w, max_h = 760, 320  # maximum display area
                img = Image.open(img_path)
                img.thumbnail((max_w, max_h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.lbl_image.config(image=photo)
                self._photo_image_ref = photo  # keep reference
                self.image_frame.pack(fill="both", expand=False)
            except Exception as e:
                # If Pillow fails for some reason, hide image and show an error in feedback
                self.lbl_image.config(image="")
                self.image_frame.pack_forget()
                self.lbl_feedback.config(text=f"(Failed to load image: {e})", foreground="orange")
        else:
            # No image for this question
            self.lbl_image.config(image="")
            self.image_frame.pack_forget()

        # Clear previous choice widgets
        for w in self.choice_widgets:
            w.destroy()
        self.choice_widgets.clear()
        self.choice_vars.clear()
        self.lbl_feedback.config(text="")

        # Multi vs single answer
        multi = len(q['correct']) > 1

        if multi:
            for i, choice in enumerate(q['choices']):
                var = tk.BooleanVar(value=False)
                cb = ttk.Checkbutton(self.frame_choices, text=choice, variable=var)
                cb.pack(anchor="w", pady=2, padx=10)
                self.choice_vars.append(var)
                self.choice_widgets.append(cb)
        else:
            sel = tk.IntVar(value=-1)
            self.choice_vars.append(sel)
            for i, choice in enumerate(q['choices']):
                rb = ttk.Radiobutton(self.frame_choices, text=choice, variable=sel, value=i)
                rb.pack(anchor="w", pady=2, padx=10)
                self.choice_widgets.append(rb)

        self.lbl_progress.config(text=f"Question: {self.index+1} / {len(self.questions)}")
        self.lbl_score.config(text=f"Score: {self.score}")
        self.progress['maximum'] = len(self.questions)
        self.progress['value'] = self.index
        self.btn_next.config(state="normal" if self.index < len(self.questions)-1 else "disabled")
        self.btn_prev.config(state="normal" if self.index > 0 else "disabled")
        self.btn_submit.config(state="normal")

    def get_selected_answers_texts(self):
        q = self.questions[self.index]
        if len(q['correct']) > 1:
            chosen = [ q['choices'][i] for i,var in enumerate(self.choice_vars) if var.get() ]
            return chosen
        else:
            sel = self.choice_vars[0].get()
            if isinstance(sel, int) and sel >= 0 and sel < len(q['choices']):
                return [ q['choices'][sel] ]
            else:
                return []

    def submit_answer(self):
        q = self.questions[self.index]
        chosen_texts = self.get_selected_answers_texts()
        if not chosen_texts:
            messagebox.showinfo(APP_TITLE, "Please select an answer (or answers).")
            return

        correct_texts = [c for c in q['correct']]

        if set(chosen_texts) == set(correct_texts):
            self.lbl_feedback.config(text="✅ Correct!", foreground="green")
            self.score += 1
        else:
            self.lbl_feedback.config(text="❌ Incorrect.\nCorrect: " + ", ".join(correct_texts), foreground="red")

        self.answered_count += 1
        self.lbl_score.config(text=f"Score: {self.score}")
        self.btn_submit.config(state="disabled")

        if self.index == len(self.questions) - 1:
            self.show_final_score()

    def next_question(self):
        if self.index < len(self.questions) - 1:
            self.index += 1
            # Re-enable submit when moving to next
            self.btn_submit.config(state="normal")
            self.show_question()

    def prev_question(self):
        if self.index > 0:
            self.index -= 1
            # Re-enable submit when moving back
            self.btn_submit.config(state="normal")
            self.show_question()

    def show_final_score(self):
        total = len(self.questions)
        correct = self.score
        percentage = (correct / total) * 100 if total > 0 else 0.0
        msg = f"You answered {correct}/{total} correctly ({percentage:.1f}%)."
        messagebox.showinfo("Final Score", msg)

    def on_quit(self):
        if messagebox.askyesno(APP_TITLE, "Are you sure you want to quit?"):
            self.destroy()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
