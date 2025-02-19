import requests


url = "https://opentdb.com/api.php?amount=1&category=17&type=multiple"

response = requests.get(url)
data = response.json()

question_data = data["results"][0]
question = question_data["question"]
correct_answer = question_data["correct_answer"]

print("Science Trivia Question:", question)
print("Answer:", correct_answer)