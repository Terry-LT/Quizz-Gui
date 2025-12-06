import pandas as pd


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

def read_quiz(questions):
    for index, q in enumerate(questions):
        answered = False
        while not answered:
            print("----")
            print("Choose the correct answer(s).")
            print("If multiple, separate with commas. Example: 1,3")
            print("-----")
            print(f"Q {index+1}: {q['type']}")
            print("")
            choices = {}
            for i, choice in enumerate(q['choices']):
                choices[i+1] = choice
            print(choices) # so user could see it
            user_input = input("Type right answer/asnwers:")
            #Check if there is comma
            if ',' in user_input:
                #TODO do it later
                '''try:
                    # Split the input into a list of strings
                    numbers_str = user_input.split(',')

                    # Convert each string to an integer
                    numbers = [int(num.strip()) for num in numbers_str]
                    for c in choices:
                        if c['']
                except ValueError:
                    print("Write answer correctly!")'''
                pass
            else:
                #Check if user answer is a number
                if user_input.isdigit():
                    user_chosen_answer = choices[int(user_input)]
                    if user_chosen_answer in q['correct']:
                        print("You answered right!")
                    else:
                        print("The answer is incorrect")
                        print(f"The correct answer/answers are {q['correct']}")
                    answered = True
                else:
                    print("Choose number")

if __name__ == "__main__":
    questions = get_questions("infs_1_quizz_str0_str27.csv")
    read_quiz(questions)