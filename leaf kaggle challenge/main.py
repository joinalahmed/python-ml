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
pid_label, pid_name = extract('leaf/train.csv')
pic_names = [i.name for i in os.scandir(dir_path) if i.is_file() and i.name.endswith('.jpg')]
input_shape = (96, 96)
m = input_shape[0] * input_shape[1]
n = len(set(pid_name.values()))


# cross validation of training photos

cross_val = False
delete = False

if delete:
    delete_folders()
kf_iterator = model_selection.StratifiedKFold(n_splits=5, shuffle=True, random_state=1)  # Stratified
train_x = list(pid_name.keys())  # leaf id
train_y = list(pid_name.values())  # leaf species names

for train_index, valid_index in kf_iterator.split(train_x, train_y):

    leaf_images = dict()  # temp dictionary of re-sized leaf images
    train = list()  # array of image and label in 1D array
    valid = list()  # array of image and label in 1D array

    train_id = [train_x[idx] for idx in train_index]
    valid_id = [train_x[idx] for idx in valid_index]

    for filename in pic_names:

        pid = int(filename.split('.')[0])
        leaf_images[pid] = pic_resize(dir_path + filename, size=input_shape, pad=True)

        if pid in train_id:
            directory = dir_path + 'train/' + pid_name[pid]
            train.append((np.array(leaf_images[pid]).flatten(), np.array(pid_label[pid])))

        elif pid in valid_id:
            directory = dir_path + 'validation/' + pid_name[pid]
            valid.append((np.array(leaf_images[pid]).flatten(), np.array(pid_label[pid])))

        else:
            directory = dir_path + 'test'

        if not os.path.exists(directory):
            os.makedirs(directory)

    train = np.array(train)
    valid = np.array(valid)

    if not cross_val:
        break

# load image into tensor

# create batches
batches = batch_iter(data=train, batch_size=50, num_epochs=1000)

# setting up tf Session


def main():

    sess = tf.Session()
    with sess.as_default():

        # declare placeholders

        x = tf.placeholder(dtype=tf.float32, shape=[None, m], name='feature')  # pixels as features
        y_ = tf.placeholder(dtype=tf.float32, shape=[None, n], name='label')  # 99 classes in 1D tensor

        # declare variables

        # Variables
        W = tf.Variable(tf.zeros([m, n]))
        b = tf.Variable(tf.zeros([n]))

        init = tf.global_variables_initializer()
        sess.run(init)

        y = tf.matmul(x, W) + b

        # loss function
        cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(y, y_))
        train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)



        valid_x = np.array([i[0] for i in valid])
        valid_y = np.array([i[1] for i in valid])

        for batch in batches:
            x_batch, y_batch = zip(*batch)
            x_batch = np.array(x_batch)
            y_batch = np.array(y_batch)
            train_step.run(feed_dict={x: x_batch, y_: y_batch})

            # eval
            correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))

            accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

            print(accuracy.eval(feed_dict={x: valid_x, y_: valid_y}))


if __name__ == '__main__':
    main()
