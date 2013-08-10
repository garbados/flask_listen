from nltk import word_tokenize, pos_tag

def tokenize(row):
    row['value'] = word_tokenize(row['value'])
    return row

def tag(row):
    tokens = word_tokenize(row['value'])
    row['value'] = [dict(token=tag[0], pos=tag[1]) for tag in pos_tag(tokens)]
    return row