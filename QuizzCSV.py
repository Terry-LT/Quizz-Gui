import pandas as pd
import os
import sys
import tkinter as tk
from tkinter import filedialog

import random

def shuffle_quiz(questions):
    # Shuffle the order of questions
    random.shuffle(questions)

    # Shuffle the choices for each question
    for q in questions:
        random.shuffle(q['choices'])

    return questions

def get_file_path():
    # Hide the main tkinter window
    root = tk.Tk()
    root.withdraw()

    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    return file_path

def get_questions(path):
    df = pd.read_csv(path, encoding="utf-8", sep=",")  # tab-separated (looks like TSV in your example)
    questions = []
    for _, row in df.iterrows():
        question = {
            "type": row["Question Type"],
            "title": row["Question Title"],
            "choices": [c.strip() for c in row["Choices"].split(",")],
            # Split correct answers by comma, strip spaces
            "correct": [c.strip() for c in row["Correct Answer(s)"].split(",")]
        }
        questions.append(question)
    return questions
def clear_console():
    input("Press to continue...")
    os.system('cls' if os.name == 'nt' else 'clear')

def count_score(total_questions,correct_answers):
    percentage = (correct_answers / total_questions-1) * 100
    print(f"You answered {correct_answers}/{total_questions} correctly ({percentage:.1f}%).")
    input("Press to left...")
    sys.exit()

def read_quiz(questions):
    score = 0
    for index, q in enumerate(questions):
        print(f"Question: {index + 1}/{len(questions)}")
        print(f"Score: {score}")
        answered = False
        while not answered:
            print("\n" + "=" * 50)  # separator
            print("Choose the correct answer(s).")
            print("If multiple, separate with commas. Example: 1,3")
            print("-" * 50)
            print(f"Q {index + 1}: {q['type']}")
            print(q['title'])
            print("-" * 50)

            # print choices clearly
            for i, choice in enumerate(q['choices'], 1):
                print(f"{i}. {choice}")

            print("-" * 50)
            user_input = input("Type right answer/answers: ")

            # Existing logic remains unchanged
            if ',' in user_input:
                # Multiple answers input
                numbers = [num.strip() for num in user_input.split(",")]
                valid = True
                try:
                    numbers = [int(num) for num in numbers]
                except ValueError:
                    valid = False

                if not valid or any(num < 1 or num > len(q['choices']) for num in numbers):
                    print("⚠️  Invalid input! Use numbers from the list, separated by commas.")
                    continue

                # Check answers
                chosen_answers = [q['choices'][num - 1] for num in numbers]
                if set(chosen_answers) == set(q['correct']):
                    print("✅ Correct!\n")
                    score+=1
                    clear_console()
                else:
                    print("❌ Incorrect!")
                    print("Correct answer(s):")
                    for ans in q['correct']:
                        print(f" - {ans}")
                    clear_console()
                answered = True
            else:
                if user_input.isdigit():
                    user_chosen_answer = q['choices'][int(user_input)-1]
                    print(user_chosen_answer)
                    if user_chosen_answer in q['correct']:
                        print("You answered right!")
                        score += 1
                        clear_console()
                    else:
                        print("The answer is incorrect")
                        print("Correct answer/answers:")
                        for ans in q['correct']:
                            print(f" - {ans}")
                        clear_console()
                    answered = True
                else:
                    print("Choose a number from the list")
    count_score(len(questions),score)
if __name__ == "__main__":
    path = get_file_path()
    questions = get_questions(path)
    while True:
        user_input = input("Shuffle questions and answers? (Y/N):")
        if user_input.lower().strip() == "y":
            read_quiz(
                shuffle_quiz(questions)
            )
            break
        else:
            read_quiz(questions)
            break
