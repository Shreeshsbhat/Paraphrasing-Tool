import sys
import numpy as np
from seq2seq import Seq2seq

# %pylab inline
from inference import predict_paraphrase
sentence=sys.argv[1]
# print(sentence)
sentence=predict_paraphrase(sentence, .1)
print(sentence.replace('</S>',''))