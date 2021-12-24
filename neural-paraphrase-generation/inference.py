import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
# tf.get_logger().setLevel('ERROR')
from seq2seq import Seq2seq
from data_handler import Data
from train import FLAGS

from tensorflow.python import debug as tf_debug
from tensorflow.contrib.learn import learn_runner

tf.logging.set_verbosity(tf.logging.INFO)




run_config = tf.contrib.learn.RunConfig()
run_config = run_config.replace(model_dir=FLAGS.experiment_dir)

data = Data(FLAGS)
data.initialize_word_vectors()

input_fn, _ = data.make_input_fn()
format_fn = lambda seq: ' '.join([data.rev_vocab.get(x, '<UNK>') for x in seq])

model = Seq2seq(data.vocab_size, FLAGS, data.embeddings_mat)
estimator = tf.estimator.Estimator(model_fn=model.make_graph,
                                   config=run_config,
                                   params=FLAGS)


def predict_feed_fn(phrase):
    tokens = data.tokenize_and_map(phrase, mode='test') + [data.END_TOKEN]
    def feed_fn():
        return {
        'source_in:0': [tokens]
        }
    return feed_fn

def predict_paraphrase(phrase, sigma):

    model.sigma = sigma
    preds = estimator.predict(input_fn=input_fn, hooks=[tf.train.FeedFnHook(predict_feed_fn(phrase))])
    return format_fn(preds.next())
