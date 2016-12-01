import os
import pandas as pd
import numpy as np
import warnings
from utils import delete_folders, extract, pic_resize, batch_iter
from GradientDescent import GradientDescent
from sklearn import model_selection
import tensorflow as tf
warnings.filterwarnings('ignore')

# coding: utf-8

__author__ = 'Ming Li'

"""This application forms a submission from Ming Li in regards to leaf kaggle challenge challenge on Kaggle community"""

# params

dir_path = 'leaf/images/'
id_label, id_name, mapping = extract('leaf/train.csv')
pic_names = [i.name for i in os.scandir(dir_path) if i.is_file()]
input_shape = (96, 96)
m = input_shape[0] * input_shape[1]
n = len(set(id_label.values()))

# cross validation of training photos

cross_val = False

kf_iterator = model_selection.StratifiedKFold(n_splits=5, shuffle=True, random_state=1)  # Stratified
train_x = list(id_name.keys())  # leaf id
train_y = list(id_name.values())  # leaf species names

for train_index, valid_index in kf_iterator.split(train_x, train_y):

    leaf_images = dict()  # temp dictionary of resized leaf images
    array_label = list()  # array of image and label of species id

    train_id = [train_x[i] for i in train_index]
    valid_id = [train_x[i] for i in valid_index]

    for name in pic_names:

        leaf_id = int(name.split('.')[0])
        leaf_images[leaf_id] = pic_resize(dir_path + name, size=input_shape, pad=True)

        if leaf_id in train_id:
            directory = dir_path + 'train/' + id_name[leaf_id]
            array_label.append((np.array(leaf_images[leaf_id]).flatten(), id_label[leaf_id]))
        elif leaf_id in valid_id:
            directory = dir_path + 'validation/' + id_name[leaf_id]
            array_label.append((np.array(leaf_images[leaf_id]).flatten(), id_label[leaf_id]))

        else:
            directory = dir_path + 'test'
        if not os.path.exists(directory):
            os.makedirs(directory)

        leaf_images[leaf_id].save(directory+'/' + name)

    data = np.array(array_label)

    if not cross_val:
        break


# create batches
batches = batch_iter(data=data, batch_size=50, num_epochs=10)

# setting up tf Session

tf.device("/cpu:0")
sess = tf.Session()

# declare placeholders

x = tf.placeholder(dtype=tf.float32, shape=[None, m], name='feature')
y_ = tf.placeholder(dtype=tf.float32, shape=[None, n], name='label')

# declare variables

# Variables
W = tf.Variable(tf.zeros([m, n]))
b = tf.Variable(tf.zeros([n]))

init = tf.global_variables_initializer()

y = tf.matmul(x, W) + b

# loss function
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(y, y_))
train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)

for batch in batches:
    x_batch, y_batch = zip(*batch)
    train_step.run(feed_dict={x: x_batch, y_: y_batch})

# eval
correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))

accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

print(accuracy.eval(feed_dict={x: , y_: }))



sess.run(init)
sess.close()

