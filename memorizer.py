import sys
import random
import json
import argparse

class Record:

    def __init__(self, question_word, answer_word, description, initial_count, count=None):
        self.question_word = question_word
        self.answer_word = answer_word
        self.description = description

        self.initial_count = initial_count
        self.count = count if count else initial_count

    def check(self, commands):
        normal="\033[0m"
        bold="\033[1;4m"
        success="\033[1;32m"
        error="\033[1;91m"

        sys.stdout.write("{}{}{}".format(bold, self.question_word, normal))
        sys.stdout.write(" ({})".format(self.description) if self.description else "")
        sys.stdout.write("?")
        answer = input(" >>> ").strip()

        if answer in commands:
            return answer

        if answer == self.answer_word:
            self.count -= 1
            sys.stdout.write("{}Correct :){}\n".format(success, normal))
        else:
            self.count = self.initial_count
            sys.stdout.write("{}Wrong :/{} (correct answer: {}{}{})\n".format(error, normal, bold, self.answer_word, normal))

        return None

    def is_known(self):
        return self.count < 1

    def get_count(self):
        return self.count

def save(d, filepath):
    with open(filepath, 'w') as f:
        for record in d:
            f.write(json.dumps(record.__dict__))
            f.write("\n")

def filter(data):
    return [record for record in data if not record.is_known()]

def get_total_count(data):
    return sum([record.get_count() for record in data])

def split(line):
    merge = True
    values = [""]
    for value in line.strip().split(' '):
        if merge:
            values[-1] += ' '
            values[-1] += value
        else:
            values.append(value)

        if value.endswith('\\'):
            values[-1] = values[-1][:-1]

        merge = value.endswith('\\') or len(values) >= 3

    values[0] = values[0].strip()

    return values

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data", metavar="DATA_FILE", help="The input data file.")
    parser.add_argument("retries", metavar="RETRIES", default=3, help="The number of times a term should be asked before it is considered as known.")
    args = parser.parse_args()

    data = []
    with open(args.data, 'r') as input_file:
        for line in input_file:
            if line.startswith('{'):
                # JSON record
                d = json.loads(line)
                data.append(Record(question_word=d["question_word"],
                    answer_word=d["answer_word"],
                    description=d["description"],
                    initial_count=int(args.retries),
                    count=d["count"]))
            else:
                # space-separated line
                d = split(line)
                data.append(Record(question_word=d[0],
                    answer_word=d[1],
                    description=d[2] if len(d) > 2 else "",
                    initial_count=int(args.retries)))

    total_count = get_total_count(data)
    while len(filter(data)) > 0:
        record = random.choice(filter(data))
        
        progress = float(get_total_count(data)) * 100 / total_count
        sys.stdout.write("[{0:.2f}%] ".format(progress))
        command = record.check(["(save)"])

        if command == "(save)":
            save(data, "results.jsons")
            break

