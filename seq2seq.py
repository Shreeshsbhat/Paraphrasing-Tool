import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from tensorflow.contrib import layers

class Seq2seq:
    def __init__(self, vocab_size, FLAGS, embeddings=None, sigma=0):
        self.FLAGS = FLAGS
        self.vocab_size = vocab_size
        self.embeddings_mat = embeddings
        self.sigma = sigma

        # Encoding
    def encode(self, seq, reuse=None):
        # input_lengths  = tf.reduce_sum(tf.to_int32(tf.not_equal(seq, 1)), 1)
        if self.embeddings_mat is not None:
            input_embed = layers.embed_sequence(
                        seq,
                        vocab_size=self.vocab_size,
                        embed_dim = self.embed_dim,
                        initializer = tf.constant_initializer(self.embeddings_mat, dtype=tf.float32),
                        trainable = False,
                        scope = 'embed',
                        reuse = reuse
                        )
        else:
            input_embed    = layers.embed_sequence(seq,
                                                   vocab_size=self.vocab_size,
                                                   embed_dim = self.embed_dim,
                                                   scope = 'embed',
                                                   reuse = reuse)
        forward_cell = tf.contrib.rnn.LSTMCell(num_units=self.num_units / 2, reuse=reuse)
        backward_cell = tf.contrib.rnn.LSTMCell(num_units=self.num_units / 2, reuse=reuse)
        # encoder_outputs, encoder_final_state = tf.nn.dynamic_rnn(cell, input_embed, dtype=tf.float32)
        # encoder_final_state_vec = tf.nn.l2_normalize(tf.concat(encoder_final_state, 1), 1)
        encoder_outputs, encoder_states = tf.nn.bidirectional_dynamic_rnn(
            forward_cell, backward_cell, input_embed, dtype=tf.float32
        )
        encoder_states = tf.nn.rnn_cell.LSTMStateTuple(
            c = tf.concat((encoder_states[0][0], encoder_states[1][0]), 1),
            h = tf.concat((encoder_states[0][1], encoder_states[1][1]), 1)
        )
        encoder_final_state_vec = tf.nn.l2_normalize(tf.concat(encoder_states, 1), 1)
        return encoder_states, encoder_final_state_vec
        # return encoder_outputs, encoder_final_state, input_lengths

    def get_paraphrase(self, encoder_out, scope, sigma):

        # From the encoder
        encoder_state = encoder_out[0]

        # Add some noise
        noise1 = tf.random_normal(tf.shape(encoder_state[0]), stddev=sigma)
        noise2 = tf.random_normal(tf.shape(encoder_state[1]), stddev=sigma)
        new_encoder_state = tf.nn.rnn_cell.LSTMStateTuple(
            c=encoder_state[0] + noise1,
            h=encoder_state[1] + noise2
        )

        # Helper
        helper = tf.contrib.seq2seq.GreedyEmbeddingHelper(
            self.embeddings,
            start_tokens=tf.to_int32(self.start_tokens),
            end_token=1
            )

        # Decoder is partially based on @ilblackdragon//tf_example/seq2seq.py
        with tf.variable_scope(scope, reuse=True):
            cell = tf.contrib.rnn.LSTMCell(num_units=self.num_units)
            out_cell = tf.contrib.rnn.OutputProjectionWrapper(cell, self.vocab_size, reuse=True)
            decoder = tf.contrib.seq2seq.BasicDecoder(
                cell=out_cell, helper=helper,
                initial_state=new_encoder_state)
            outputs = tf.contrib.seq2seq.dynamic_decode(
                decoder=decoder, output_time_major=False,
                impute_finished=True, maximum_iterations=self.FLAGS.output_max_length + 1)
            return outputs[0]

    def decode(self, encoder_out, scope, output, reuse=None):

        # From the encoder
        encoder_state = encoder_out[0]

        # Perform the embedding
        # if mode=='train':
        #     if output is None:
        #         raise Exception('output must be provided for mode=train')
        train_output   = tf.concat([tf.expand_dims(self.start_tokens, 1), output], 1)
        output_lengths = tf.reduce_sum(tf.to_int32(tf.not_equal(train_output, 1)), 1)
        output_embed   = layers.embed_sequence(
            train_output,
            vocab_size=self.vocab_size,
            embed_dim = self.embed_dim,
            scope = 'encode/embed', reuse = True)

        # Prepare the helper
        # if mode=='train':
        #     helper = tf.contrib.seq2seq.TrainingHelper(output_embed, output_lengths)
        # if mode=='predict':
        #     helper = tf.contrib.seq2seq.GreedyEmbeddingHelper(
        #         self.embeddings,
        #         start_tokens=tf.to_int32(self.start_tokens),
        #         end_token=1
        #         )
        helper = tf.contrib.seq2seq.TrainingHelper(output_embed, output_lengths)

        # Decoder is partially based on @ilblackdragon//tf_example/seq2seq.py
        with tf.variable_scope(scope, reuse=reuse):
            # attention_mechanism = tf.contrib.seq2seq.BahdanauAttention(
            #     num_units=self.num_units, memory=encoder_outputs,
            #     memory_sequence_length=input_lengths)
            cell = tf.contrib.rnn.LSTMCell(num_units=self.num_units)
            # attn_cell = tf.contrib.seq2seq.AttentionWrapper(cell, attention_mechanism, attention_layer_size=self.num_units / 2)
            out_cell = tf.contrib.rnn.OutputProjectionWrapper(cell, self.vocab_size, reuse=reuse)
            decoder = tf.contrib.seq2seq.BasicDecoder(
                cell=out_cell, helper=helper,
                initial_state=encoder_state)
            outputs = tf.contrib.seq2seq.dynamic_decode(
                decoder=decoder, output_time_major=False,
                impute_finished=True, maximum_iterations=self.FLAGS.output_max_length + 1)

            return outputs[0]

    def seq_loss(self, decoding, actual):
            train_output = tf.concat([tf.expand_dims(self.start_tokens, 1), actual], 1)
            weights = tf.to_float(tf.not_equal(train_output[:, :-1], 1))
            # tf.identity(decoding.rnn_output[0], name='decoder_output')
            # tf.identity(actual[0], name='actual')
            # max_seq_length = tf.shape(decoding.rnn_output)[1]
            loss = tf.contrib.seq2seq.sequence_loss(
                            decoding.rnn_output,
                            actual,
                            # average_across_timesteps=True,
                            # average_across_batch=True,
                            weights=weights)
            return loss

    def sampled_seq_loss(self, decoding, actual):
        """
        This doesn't work
        """
        with tf.variable_scope('decode/decoder/output_projection_wrapper', reuse=True) as scope:
            kernel = tf.get_variable('kernel')
            bias = tf.get_variable('bias')
        return tf.nn.sampled_softmax_loss(
            tf.transpose(kernel),
            bias,
            tf.reshape(decoding.rnn_output, [-1, self.vocab_size]),
            tf.cast(tf.reshape(actual, [-1, 1]), dtype=tf.float32),
            num_sampled=512,
            num_classes=self.vocab_size
        )

    def sim_loss(self, enc1, enc2, label):
        scores = tf.sigmoid(tf.reduce_sum(tf.multiply(enc1, enc2), axis=1))
        loss = - tf.reduce_mean(label * tf.log(scores + .0001) + (1 - label) * tf.log(1 - scores + .001))
        return loss

    def make_graph(self,mode, features, labels, params):
        self.embed_dim = params.embed_dim
        self.num_units = params.num_units

        # Data
        source_in, source_out = features['source_in'], features['source_out']
        target_in, target_out = features['target_in'], features['target_out']
        label = features['label']

        self.batch_size     = tf.shape(source_in)[0]
        self.start_tokens   = tf.zeros([self.batch_size], dtype= tf.int64)

        with tf.variable_scope('encode'):
            source_encoder_out = self.encode(source_in)
            target_encoder_out = self.encode(target_in, reuse=True)

        # Save embeddings
        with tf.variable_scope('encode/embed', reuse=True):
            self.embeddings = tf.get_variable('embeddings')

        # Decode
        train_output_source = self.decode(source_encoder_out, 'decode', source_out)
        train_output_target = self.decode(target_encoder_out, 'decode', target_out, reuse=True)
        # pred_output_source = self.decode(source_encoder_out, 'decode', mode='predict', reuse=True)
        # pred_output_target = self.decode(target_encoder_out, 'decode', mode='predict', reuse=True)
        pred_output_source = self.get_paraphrase(source_encoder_out, 'decode', self.sigma)



        ############# Debug ##############
        # return train_output_source, source_in, source_out, target_in, target_out, label

        # Loss
        # tf.Print(train_output_source, [train_output_source.rnn_output[0]])
        # tf.Print(source, [source])
        source_loss = self.seq_loss(train_output_source, source_out)
        target_loss = self.seq_loss(train_output_target, target_out)
        sim_loss = self.sim_loss(source_encoder_out[1],
                                 target_encoder_out[1],
                                 label)

        # loss = source_loss + target_loss + sim_loss
        loss = source_loss + sim_loss



        ########## Debug #################################
        # return train_output_source, loss, source, target, label
        ##################################################



        tf.summary.scalar('source_loss', source_loss)
        # tf.summary.scalar('target_loss', target_loss)
        tf.summary.scalar('sim_loss', sim_loss)
        eval_metrics = {
            'source_loss': tf.contrib.metrics.streaming_mean(source_loss),
            'target_loss': tf.contrib.metrics.streaming_mean(target_loss),
            'sim_loss': tf.contrib.metrics.streaming_mean(sim_loss)
            }
        # + sim_loss
        # For logging
        # tf.identity(train_outputs.sample_id[0], name='train_pred')

        # train_output = tf.concat([tf.expand_dims(self.start_tokens, 1), source], 1)
        # weights = tf.to_float(tf.not_equal(train_output[:, :-1], 1))
        # loss = tf.contrib.seq2seq.sequence_loss(train_outputs.rnn_output, source, weights=weights)
        train_op = layers.optimize_loss(
            loss, tf.train.get_global_step(),
            optimizer=params.optimizer,
            learning_rate=params.learning_rate,
            summaries=['loss', 'learning_rate'])

        # tf.identity(pred_output_source.sample_id[0], name='predict')
        tf.identity(pred_output_source.sample_id[0], name='predict')
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions=pred_output_source.sample_id,
            loss=loss,
            train_op=train_op,
            eval_metric_ops=eval_metrics
        )
