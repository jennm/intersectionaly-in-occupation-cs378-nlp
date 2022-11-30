from instantiate import get_formatted_sentences
import pandas

import cohere
from cohere.classify import Example

training, testing = get_formatted_sentences()
training_data = training[0]
training_answers = training[1]
testing_data = testing[0]
testing_answers = testing[1]

co = cohere.Client('MohgsE9SoH0XAHi48tVAtgg0f9Zxaj9g0VZdg7fo')

total_data = len(testing_data)
num_data = 2500
start = 0

iterations = len(testing_data) // num_data
output_dict = {"Prediction": [], "Confidence": [], "True Value": []}
if len(testing_data) % num_data != 0:
    iterations += 1
training_examples = list()

for i in range(len(training_data)):
    if training_answers[i] == 1:
        answer = "participant"
    else:
        answer = "occupation"
    training_examples.append(Example(training_data[i], answer))


response = co.classify(
    model='large',
    inputs=testing_data[0],
    examples=training_examples[0:20])
print(response)
exit()
for i in range(iterations):

    response = co.classify(
        model='large',
        inputs=testing_data[num_data *
                            i: min(num_data * (i + 1), len(testing_data))],
        examples=training_examples)
    print(response)
# print('The confidence levels of the labels are: {}'.format(response.classifications))
# print(len(answers))
# print(type(response.classifications))
    output = response.classifications

    for j in range(len(output)):
        output_dict["Prediction"].append(output[j].prediction)
        output_dict["Confidence"].append(output[j].confidence)
        if testing_answers[num_data * i + j] == 1:
            answer = "participant"
        else:
            answer = "occupation"
        output_dict["True Value"].append(answer)


dataFrame = pandas.DataFrame(output_dict)
dataFrame.to_csv("results.csv")
# for prediction, confidence in response.classifications.enumerate():
#     print(prediction, confidence)
# print(answers[0:10])
