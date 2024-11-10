import random


OutputLen = 500

with open('words_alpha.txt') as words_file:
    words_text = words_file.read()
with open('common_words.txt') as words_file:
    common_words = words_file.read()
with open('important_words.txt') as words_file:
    added_words = words_file.read()

words = words_text.split('\n')
added_words = added_words.split('\n')
common_words = common_words.split('\n')

output_text = []
for _ in range(OutputLen):
    if random.randint(0,1) == 0:
        output_text.append(random.choice(added_words))
    else:
        if random.randint(0,5) == 2:
            output_text.append(random.choice(words))
        else:
            output_text.append(random.choice(common_words))

output_text = " ".join(output_text)

with open('READ_THIS_WHILST_RECORDING.txt','w') as output_file:
    output_file.write(output_text)
