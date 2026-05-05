from typing import TypedDict

class TextAttributes(TypedDict):
    word_count: int
    unique_words: set[str]
    average_word_length: float
    longest_word: str

def calculate_text_attributes(input_text: str) -> TextAttributes:
    split_text = input_text.split()

    get_unique = set(input_text.split())

    sum = 0
    for item in split_text:
        sum += len(item)

    if len(split_text):
        avg_length = sum/len(split_text)
    else:
        avg_length = 0

    max_length = 0
    word = ""
    for item in split_text:
        length = len(item)
        if max_length < length:
            max_length = length
            word = item
    
    return {
        "word_count": len(split_text), "unique_words": len(get_unique), "average_word_length": avg_length, "longest_word": word,
    }