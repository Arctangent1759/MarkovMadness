import argparse
from urllib import urlopen
from re import sub
from random import random

kHolyBible="http://www.gutenberg.org/cache/epub/10/pg10.txt"
kTomSawyer="http://www.gutenberg.org/cache/epub/74/pg74.txt"

kAllPunctuation = [
    ".",
    "?",
    ",",
    ":",
    ";",
    "\"",
    "(",
    ")",
    "!",
    ]
kSentenceTerminators = [
    ".",
    "?",
    "!",
]

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
      r"\"",
      r"_",
      r"\(",
      r"\)",
      ]
  punctuation = [
      ".",
      "?",
      ",",
      ":",
      ";",
      "!",
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

# Returns a distribution of words that start sentences.
def GetSentenceSeeds(text, n_gram_parameter, punctuation = ['.', '?', '!']):
  text = ". " + text
  word_list = text.split(" ")
  word_starts = [tuple(word_list[i+1:i + n_gram_parameter+1]) for i in range(len(word_list) - n_gram_parameter) if word_list[i] in punctuation]
  word_starts = filter(lambda x:False not in [(i not in (punctuation + ["(",")"])) for i in x], word_starts)
  out = {}
  for word in set(word_starts):
    out[word] = float(word_starts.count(word))/float(len(word_starts))
  return out

# Takes a distribution ({string:float}) and returns a result(string) based on
# sampling of the distribution.
def SampleDist(dist):
  val = random();
  for key in dist:
    if val < dist[key]:
      return key
    else:
      val -= dist[key]
  assert False, "Distribution probabilities don't add up to 1."

def ReconstructSentences(tokens):
  for i in range(len(tokens)):
    if i == 0  or tokens[i - 1] in kSentenceTerminators:
      if len(tokens[i]) != 0:
        tokens[i] = tokens[i][0].upper() + tokens[i][1:]
  out = " ".join(tokens)
  for punctuation in kAllPunctuation:
    out = out.replace(" "+punctuation, punctuation)
  return out

class MarkovSentenceGenerator:
  # Inits a MarkovSentenceGenerator from source selector sources.
  punctuation = [".", "?", "!"]
  def __init__(self, sources, n_gram_parameter):
    training_data = " ".join([GetSource(source) for source in sources])
    self.dist = GetTokenDictionary(training_data, n_gram_parameter)
    self.start_dist = GetSentenceSeeds(training_data, n_gram_parameter)
    self.n_gram_parameter = n_gram_parameter

  def GetSentences(self, n):
    tokens_out = list(SampleDist(self.start_dist))
    while n > 0:
      key = tuple(tokens_out[len(tokens_out) - self.n_gram_parameter:])
      next_token = SampleDist(self.dist[key])
      if next_token in self.punctuation:
        n-=1
      tokens_out.append(next_token)
    return ReconstructSentences(tokens_out)

def main():
  parser = argparse.ArgumentParser(description = "Markov Madness")
  parser.add_argument('-k', dest='NumSentences', type=int, default=1,
      help='How many sentences to generate.')
  parser.add_argument('-n', dest='NGramParameter', type=int, default=2,
      help='Learning Parameter. The number of words to consider at each cycle.')
  parser.add_argument('training_data', type=str, nargs='+')
  args = parser.parse_args()
  print MarkovSentenceGenerator(args.training_data,args.NGramParameter).GetSentences(args.NumSentences)

if __name__ == "__main__":
  main()
