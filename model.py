from instantiate import get_formatted_sentences
import pandas

import cohere
from cohere.classify import Example

training, testing = get_formatted_sentences()
training_occupation_sent = training[2]
training_occupation_some1 = training[3]
training_participant_sent = training[0]
training_participant_some1 = training[1]
testing_data = testing[0]
testing_answers = testing[1]
print(training)

co = cohere.Client('MohgsE9SoH0XAHi48tVAtgg0f9Zxaj9g0VZdg7fo')

total_data = len(testing_data)
num_data = 2500
start = 0

iterations = len(testing_data) // num_data
output_dict = {"Prediction": [], "Confidence": [], "True Value": []}
if len(testing_data) % num_data != 0:
    iterations += 1
training_examples = list()

training_occupation_sent.sort()
training_occupation_some1.sort()
training_participant_sent.sort()
training_participant_some1.sort()
for i in range(5):
    training_examples.append(
        Example(training_occupation_sent[i], "occupation"))
    training_examples.append(
        Example(training_participant_sent[i], "participant"))
    training_examples.append(
        Example(training_occupation_some1[i], "occupation"))
    training_examples.append(
        Example(training_participant_some1[i], "participant"))


# print(training_examples)
# print(testing_data[0])
# response = co.classify(
#     model='large',
#     inputs=[testing_data[0]],
#     # examples=[Example(
#     #     "The  technician told the customer that he could pay with cash.", "participant"), Example("Someone met with the  accountant to get help filing their taxes.", "participant"), Example("The librarian helped the child pick out a book because she liked to encourage reading.", "occupation")],
#     examples=training_examples[0:20])
# print(response)
# exit()
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
