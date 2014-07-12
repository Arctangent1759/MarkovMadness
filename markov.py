import argparse
from urllib import urlopen
from re import sub

kHolyBible="http://www.gutenberg.org/cache/epub/10/pg10.txt"
kTomSawyer="http://www.gutenberg.org/cache/epub/74/pg74.txt"

# Figures out if url is a web source or a local one, and returns the 
# appropriate textual result.
def LoadText(url):
  if url[:7] == "http://":
    return urlopen(url).read().strip()
  else:
    return open(url).read().strip()

# Removes all occurrances of the regex patterns in blacklist(string) from 
# text(string) and returns the result)(text)
def SanitizeText(text, blacklist, punctuation):
  for pattern in blacklist:
    #ugh. Inefficient. Someone plz fix.
    text = sub(pattern," ",text)
  for mark in punctuation:
    text = text.replace(mark," "+mark+" ")
  text = sub(" +"," ",text)
  return text.lower()

# Loads and sanitizes text from url(string) and returns the text(string)
def GetSource(url):
  source_raw = LoadText(url)
  blacklist = [
    r"\n",
    r"\r",
    r"\d+:\d+",
  ]
  punctuation = [
    ".",
    "?",
    ",",
    ":",
    ";",
    "\"",
    "(",
    ")",
  ]
  return SanitizeText(source_raw, blacklist, punctuation)

# Tokenizes text, splitting it into words. Returns a hash from a tuple of k 
# words to a map from the word after those k words to a number of occurrances.
# Returns a token dictionary ({string:{string:int}})
def TokenizeText(text, n):
  word_list = text.split(" ")
  out = {}
  for i in range(n,len(word_list)):
    key = tuple(word_list[i-n:i])
    value = word_list[i]
    if key in out:
      if value in out[key]:
        out[key][value] += 1
      else:
        out[key][value] = 1
    else:
      out[key] = { value:1 }
  return out

# Normalizes a token dictionary ({string:{string:int}}) to a dictionary of
# probabilities ({string:{string:float}})
def NormalizeTokenDictionary(token_dict):
  for key in token_dict:
    total = 0
    for token in token_dict[key]:
      total += token_dict[key][token]
    for token in token_dict[key]:
      token_dict[key][token] /= float(total)
  return token_dict

# Returns the normalized token dictionary from the corpora.
def GetTokenDictionary(text,n):
  return NormalizeTokenDictionary(TokenizeText(text, n))

def main():
  parser = argparse.ArgumentParser(description = "Markov Madness")
  parser.add_argument('-k', dest='NumSentences', type=int, default=1,
    help='How many sentences to generate.')
  parser.add_argument('-n', dest='NGramParameter', type=int, default=2,
    help='Learning Parameter. The number of words to consider at each cycle.')
  parser.add_argument('training_data', type=str, nargs='+')
  args = parser.parse_args()

if __name__ == "__main__":
  main()
