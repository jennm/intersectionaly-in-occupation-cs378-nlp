import sys
import argparse
import pandas
import random

# This script fully instantiates the 120 templates in ../data/templates.tsv
# to generate the 720 sentences in ../data/all_sentences.tsv
# By default this script prints to stdout, and can be run with no arguments:

# python instantiate.py

races = ["", "Black ", "White ", "Asian ", "Hispanic ", "Indigenous "]
genders = ["male", "female", "neutral"]


def load_templates(path):
    fp = open(path, 'r')
    S = []
    headers = fp.readline().strip().split('\t')
    for line in fp:
        line = line.strip().split('\t')
        occupation, other_participant, answer, sentence = line[0], line[1], int(
            line[2]), line[3]
        S.append((occupation, other_participant, answer, sentence))
    return S


def generate(occupation, other_participant, answer, sentence, someone=False, context=None):
    toks = sentence.split(" ")
    occ_index = toks.index("$OCCUPATION")
    part_index = toks.index("$PARTICIPANT")
    toks[occ_index] = occupation
    if not someone:  # we are using the instantiated participant, e.g. "client", "patient", "customer",...
        toks[part_index] = other_participant
    else:  # we are using the bleached NP "someone" for the other participant
        # first, remove the token that precedes $PARTICIPANT, i.e. "the"
        toks = toks[:part_index-1]+toks[part_index:]
        # recompute participant index (it should be part_index - 1)
        part_index = toks.index("$PARTICIPANT")
        if part_index == 0:
            toks[part_index] = "Someone"
        else:
            toks[part_index] = "someone"
    NOM = "$NOM_PRONOUN"
    POSS = "$POSS_PRONOUN"
    ACC = "$ACC_PRONOUN"
    special_toks = set({NOM, POSS, ACC})
    female_map = {NOM: "she", POSS: "her", ACC: "her"}
    male_map = {NOM: "he", POSS: "his", ACC: "him"}
    neutral_map = {NOM: "they", POSS: "their", ACC: "them"}
    female_toks = [x if not x in special_toks else female_map[x] for x in toks]
    male_toks = [x if not x in special_toks else male_map[x] for x in toks]
    neutral_toks = [x if not x in special_toks else neutral_map[x]
                    for x in toks]
    male_sent, female_sent, neutral_sent = " ".join(
        male_toks), " ".join(female_toks), " ".join(neutral_toks)
    neutral_sent = neutral_sent.replace("they was", "they were")
    neutral_sent = neutral_sent.replace("They was", "They were")
    return male_sent, female_sent, neutral_sent


def get_formatted_sentences(train_test_split=0.8, race_blind=True, to_print=False):
    sentence_path = "winogender-schemas/data/templates.tsv"
    S = load_templates(sentence_path)

    data = list()
    answers = list()
    formatted_data = {'Sentence': [], 'Ocuppation Race': [],
                      'Other Participant Race': [], 'Gender': []}

    random.shuffle(S)
    split_point = int(len(S) * train_test_split)
    # training_data = list()
    testing_data = list()
    training_occupation_sent = list()
    training_occupation_some1 = list()
    training_participant_sent = list()
    training_participant_some1 = list()
    # training_answers = list()
    testing_answers = list()
    count = 0

    for s in S:
        _occupation, _other_participant, answer, sentence = s
        print(answer)
        male_sent, female_sent, neutral_sent = generate(
            _occupation, _other_participant, answer, sentence)
        male_sentid, female_sentid, neutral_sentid = [_occupation+'.'+_other_participant+'.'+str(
            answer)+'.'+gender+".txt" for gender in ["male", "female", "neutral"]]

        male_sent_some1, female_sent_some1, neutral_sent_some1 = generate(
            _occupation, _other_participant, answer, sentence, someone=True)
        male_sentid_some1, female_sentid_some1, neutral_sentid_some1 = [
            _occupation+'.'+"someone"+'.'+str(answer)+'.'+gender+".txt" for gender in ["male", "female", "neutral"]]

        if count % 3 == 0:
            sent = male_sent
            some1 = male_sent_some1
        elif count % 3 == 1:
            sent = female_sent
            some1 = female_sent_some1
        else:
            sent = neutral_sent
            some1 = neutral_sent_some1

        if answer:
            training_participant_sent.append(sent)
            training_participant_some1.append(some1)
        else:
            training_occupation_sent.append(sent)
            training_occupation_some1.append(some1)

        for race1 in races:
            for race2 in races:
                occupation = f"{race1} {_occupation}"
                other_participant = f"{race2} {_other_participant}"

                male_sent, female_sent, neutral_sent = generate(
                    occupation, other_participant, answer, sentence)
                male_sentid, female_sentid, neutral_sentid = [occupation+'.'+other_participant+'.'+str(
                    answer)+'.'+gender+".txt" for gender in ["male", "female", "neutral"]]

                male_sent_some1, female_sent_some1, neutral_sent_some1 = generate(
                    occupation, other_participant, answer, sentence, someone=True)
                male_sentid_some1, female_sentid_some1, neutral_sentid_some1 = [
                    occupation+'.'+"someone"+'.'+str(answer)+'.'+gender+".txt" for gender in ["male", "female", "neutral"]]

                if to_print:
                    # other participant is specific
                    print(male_sentid+"\t"+male_sent)
                    print(female_sentid+"\t"+female_sent)
                    print(neutral_sentid+"\t"+neutral_sent)

                    # other participant is "someone"
                    print(male_sentid_some1+"\t"+male_sent_some1)
                    print(female_sentid_some1+"\t"+female_sent_some1)
                    print(neutral_sentid_some1+"\t" +
                          neutral_sent_some1+"\t"+str(answer))

                testing_data.append(male_sent)
                formatted_data["Sentence"].append(male_sent)
                formatted_data['Gender'].append('male')
                testing_data.append(female_sent)
                formatted_data["Sentence"].append(female_sent)
                formatted_data['Gender'].append('female')
                testing_data.append(neutral_sent)
                formatted_data["Sentence"].append(neutral_sent)
                formatted_data['Gender'].append('neutral')
                testing_data.append(male_sent_some1)
                formatted_data["Sentence"].append(male_sent_some1)
                formatted_data['Gender'].append('male')
                testing_data.append(female_sent_some1)
                formatted_data["Sentence"].append(female_sent_some1)
                formatted_data['Gender'].append('female')
                testing_data.append(neutral_sent_some1)
                formatted_data["Sentence"].append(neutral_sent_some1)
                formatted_data['Gender'].append('neutral')
                for i in range(6):
                    formatted_data["Ocuppation Race"].append(race1)
                    formatted_data["Other Participant Race"].append(race2)
                    testing_answers.append(answer)

    data_frame = pandas.DataFrame(formatted_data)
    data_frame.to_csv('formatted_data_split.csv')

    return [training_participant_sent, training_participant_some1, training_occupation_sent, training_occupation_some1], [testing_data, testing_answers]


if __name__ == "__main__":
    get_formatted_sentences(True)
