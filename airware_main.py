from data import Read_Data
import numpy as np
from keras.layers import Reshape, merge, concatenate
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D, Conv1D, MaxPooling1D
from keras.preprocessing.image import ImageDataGenerator
from keras.regularizers import l2
from keras.models import Input, Model
from keras import backend as K

from sklearn.model_selection import LeaveOneGroupOut, StratifiedShuffleSplit
import sklearn.metrics as mt

import matplotlib.pyplot as plt


# @TODO: Add args to grid search model parameters
def split_model_1():
    l2_val = l2(0.001)
    image_input = Input(
        shape=(input_shape[0], input_shape[1] - 2, 1), dtype='float32')
    x = Reshape(target_shape=(input_shape[0], input_shape[1] - 2))(image_input)
    # Convolution Layer 1
    x = Conv1D(8, 3, padding='same', activation='relu',
               kernel_initializer='he_uniform', kernel_regularizer=l2_val)(x)
    x = MaxPooling1D(2)(x)
    # Convolution Layer 2
    x = Conv1D(16, 3, padding='same', activation='relu',
               kernel_initializer='he_uniform', kernel_regularizer=l2_val)(x)
    # x = Conv1D(1, 3, padding='same', activation='relu',kernel_initializer='he_uniform',kernel_regularizer=l2_val)(x)
    image_x = Flatten()(MaxPooling1D(2)(x))

    ir_input = Input(shape=(input_shape[0], 2, 1), dtype='float32')
    x = Reshape(target_shape=(input_shape[0], 2))(ir_input)
    # Convolution Layer 1
    x = Conv1D(2, 3, padding='same', activation='relu',
               kernel_initializer='he_uniform', kernel_regularizer=l2_val)(x)
    x = MaxPooling1D(2)(x)
    # Convolution Layer 2
    x = Conv1D(2, 3, padding='same', activation='relu',
               kernel_initializer='he_uniform', kernel_regularizer=l2_val)(x)
    ir_x = Flatten()(MaxPooling1D(2)(x))

    x = concatenate([image_x, ir_x])
    # x = Flatten()(x)
    # Dense Network - MLP
    x = Dense(100, activation='relu', kernel_initializer='he_normal',
              kernel_regularizer=l2_val)(x)
    preds = Dense(NUM_CLASSES, activation='softmax',
                  kernel_initializer='glorot_uniform')(x)

    model = Model([image_input, ir_input], preds)
    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['acc'])
    return model


def create_generator(XI, Y, batch_size=64):
    X = XI[0]
    I = XI[1]
    while True:
        # suffled indices
        idx = np.random.permutation(X.shape[0])
        # create image generator
        datagenSpec = ImageDataGenerator(
            featurewise_center=False,  # set input mean to 0 over the dataset
            samplewise_center=False,  # set each sample mean to 0
            featurewise_std_normalization=False,  # divide inputs by std of the dataset
            samplewise_std_normalization=False,  # divide each input by its std
            zca_whitening=False,  # apply ZCA whitening
            # 180,  # randomly rotate images in the range (degrees, 0 to 180)
            rotation_range=0,
            # 0.1,  # randomly shift images horizontally (fraction of total
            # width)
            width_shift_range=0.0,
            # 0.1,  # randomly shift images vertically (fraction of total
            # height)
            height_shift_range=0.1,
            horizontal_flip=False,  # randomly flip images
            vertical_flip=False)  # randomly flip images

        batchesSpec = datagenSpec.flow(
            X[idx], Y[idx], batch_size=batch_size, shuffle=False)

        # create image generator
        datagenIR = ImageDataGenerator(
            featurewise_center=False,  # set input mean to 0 over the dataset
            samplewise_center=False,  # set each sample mean to 0
            featurewise_std_normalization=False,  # divide inputs by std of the dataset
            samplewise_std_normalization=False,  # divide each input by its std
            zca_whitening=False,  # apply ZCA whitening
            # 180,  # randomly rotate images in the range (degrees, 0 to 180)
            rotation_range=0,
            # 0.1,  # randomly shift images horizontally (fraction of total
            # width)
            width_shift_range=0.0,
            # 0.1,  # randomly shift images vertically (fraction of total
            # height)
            height_shift_range=0.1,
            horizontal_flip=False,  # randomly flip images
            vertical_flip=False)  # randomly flip images

        batchesIR = datagenIR.flow(
            I[idx], Y[idx], batch_size=batch_size, shuffle=False)

        for b1, b2 in zip(batchesSpec, batchesIR):
            # print(b1[0].shape,b2[0].shape)
            yield [b1[0], b2[0]], b1[1]

        break


def write_results(train_scores, test_scores, class_names, y_hat, y_true, file_path):
    np.savez(file_path + "_Train_Scores.npz", train_scores)
    np.savez(file_path + "_Test_Scores.npz", test_scores)
    np.savez(file_path + "_Predictions.npz", y_hat)
    np.savez(file_path + "_Truth.npz", y_true)


def loso_cv(X, Y, user, lab_enc, nb_epoch=100, file_name="Exp_"):
    logo = LeaveOneGroupOut()
    batch_size = 10

    train_scores, test_scores = [], []
    train_val_hist = []
    Y_true, Y_hat = [], []
    class_names = []
    i = 1

    for train_idx, test_idx in logo.split(X, Y, user):
        print("\nUser:", i)
        i += 1
        # Train and test data - leave one subject out
        x_train, y_train = X[train_idx, :, :, :], Y[train_idx]
        x_test, y_test = X[test_idx, :, :, :], Y[test_idx]

        # Create copies of the train and test data sets
        x_train_copy, y_train_copy = x_train.copy(), y_train.copy()
        x_test_copy, y_test_copy = x_test.copy(), y_test.copy()

        # Call model function
        split_model = split_model_1()

        # steps_per_epoch = how many generators to go through per epoch
        train_val_hist.append(split_model.fit_generator(
            create_generator([x_train_copy[:, :, 0:-2, :], x_train_copy[:, :, -2:, :]], y_train_copy,
                             batch_size=batch_size), steps_per_epoch=int(len(x_train_copy) / batch_size),
            epochs=nb_epoch, verbose=0,
            validation_data=([x_test_copy[:, :, 0:-2, :], x_test_copy[:, :, -2:, :]], y_test_copy)))
        # Evaluate training scores
        train_scores.append(
            split_model.evaluate([x_train_copy[:, :, 0:-2, :], x_train_copy[:, :, -2:, :]], y_train_copy))
        # Evaluate test scores
        test_scores.append(
            split_model.evaluate([x_test_copy[:, :, 0:-2, :], x_test_copy[:, :, -2:, :]], y_test_copy))

        # Predict for test data
        yhat = np.argmax(split_model.predict([x_test_copy[:, :, 0:-2, :], x_test_copy[:, :, -2:, :]]), axis=1)
        class_names.append(lab_enc.classes_[y_test_copy])
        Y_hat.append(yhat)
        Y_true.append(y_test_copy)
        # K.clear_session()
    print("Writing results...")
    write_results(train_scores, test_scores, class_names, Y_hat, Y_true, file_name)
    return train_val_hist


def plot_train_hist(train_val_hist, file_path):
    fig, axarr = plt.subplots(1, 2, sharey=True)
    i = 1
    for item in train_val_hist:
        axarr[0].plot(item.history['loss'], label='User_' + str(i))
        axarr[1].plot(item.history['val_loss'], label='User_' + str(i))
        i += 1
    plt.legend(loc='best')
    plt.savefig(file_path + "Loss_History.png")


def run_final_model():
    global NUM_CLASSES, input_shape
    fname = "./leave_one_subject/Final_Model"
    gd = Read_Data.GestureData()
    print("Reading data")
    x, y, user, input_shape, lab_enc = gd.compile_data(nfft=4096, overlap=0.5, brange=8)
    NUM_CLASSES = len(lab_enc.classes_)

    print("Train the model")
    train_val_hist = loso_cv(x,
                             y, user,
                             lab_enc,
                             nb_epoch=5,
                             file_name=fname)
    plot_train_hist(train_val_hist, file_path=fname)
    K.clear_session()


def grid_search(nfft_try, overlap_try, brange_try):
    K.clear_session()
    # Grid Search
    for nfft_val in nfft_try:
        for overlap_val in overlap_try:
            for brange_val in brange_try:
                # Define file name to store results
                fname = "./leave_one_subject/Exp_" + str(nfft_val) + "_" + str(overlap_val) + "_" + str(brange_val)
                # Read and format data
                gd = Read_Data.GestureData()
                print("Reading data")
                x, y, user, input_shape, lab_enc = gd.compile_data(nfft=nfft_val, overlap=overlap_val,
                                                                   brange=brange_val)
                print("NFFT_Val: ", nfft_val, "Overlap_Val: ", overlap_val, "Brange_Val:", brange_val)
                print("Train the model")
                train_score, test_score, train_val_hist, class_names, y_hat, y_true = loso_cv(x,
                                                                                              y, user,
                                                                                              lab_enc,
                                                                                              nb_epoch=100,
                                                                                              file_name=fname)
                plot_train_hist(train_val_hist, file_path=fname)
                K.clear_session()


def strat_shuffle_split(X, y, split=0.3, random_state=12345):
    cv_obj = StratifiedShuffleSplit(n_splits=1, test_size=split, random_state=random_state)
    for train_idx, test_idx in cv_obj.split(X, y):
        x_add_train, y_add_train = X[train_idx, :, :, :], y[train_idx]
        x_test, y_test = X[test_idx, :, :, :], y[test_idx]

    return x_add_train, x_test, y_add_train, y_test


def user_split_cv(x, y, user, lab_enc, cv_folds=5, nb_epoch=200, file_name="Exp_"):
    logo = LeaveOneGroupOut()
    batch_size = 10
    train_score, test_score = [], []
    y_hat, y_true = [], []
    i = 0
    for train_idx, test_idx in logo.split(x, y, user):
        i += 1
        print("\nUser:", i)

        x_train, y_train = x[train_idx, :, :, :], y[train_idx]
        x_test, y_test = x[test_idx, :, :, :], y[test_idx]

        cv_train_score, cv_test_score = [], []
        cv_yhat, cv_ytrue = [], []

        for j in range(cv_folds):
            print("Fold:", j)
            seed_gen = j * 200
            # Split user test data - 60% added to the training data set
            x_add, x_test_new, y_add, y_test_new = strat_shuffle_split(x_test, y_test, split=0.4, random_state=seed_gen)

            # Add additional training data to the original
            x_train = np.vstack((x_train, x_add))
            y_train = np.vstack((y_train, y_add))

            sort_idx = np.argsort(y_test_new.reshape(-1))
            x_test_new = x_test_new[sort_idx, :, :, :]
            y_test_new = y_test_new[sort_idx]

            x_train_copy = x_train.copy()
            y_train_copy = y_train.copy()

            x_test_copy = x_test_new.copy()
            y_test_copy = y_test_new.copy()

            split_model = split_model_1()
            split_model.fit_generator(
                create_generator([x_train_copy[:, :, 0:-2, :], x_train_copy[:, :, -2:, :]], y_train_copy,
                                 batch_size=batch_size),
                steps_per_epoch=int(len(x_train_copy) / batch_size),  # how many generators to go through per epoch
                epochs=nb_epoch, verbose=0,
                validation_data=([x_test_copy[:, :, 0:-2, :], x_test_copy[:, :, -2:, :]], y_test_copy))

            cv_train_score.append(
                split_model.evaluate([x_train_copy[:, :, 0:-2, :], x_train_copy[:, :, -2:, :]], y_train_copy))
            cv_test_score.append(
                split_model.evaluate([x_test_copy[:, :, 0:-2, :], x_test_copy[:, :, -2:, :]], y_test_copy))

            y_hat_temp = np.argmax(split_model.predict([x_test_copy[:, :, 0:-2, :], x_test_copy[:, :, -2:, :]]), axis=1)
            # cv_class_names.append(lab_enc.classes_[y_test_copy])
            cv_ytrue.append(y_test_copy)
            cv_yhat.append(y_hat_temp)

        train_score.append(cv_train_score)
        test_score.append(cv_test_score)
        y_hat.append(cv_yhat)
        y_true.append(cv_ytrue)
        K.clear_session()
    write_results(train_score, test_score, y_hat, y_true, file_path=file_name)


if __name__ == '__main__':
    nfft_try = [int(4096), int(2048), int(1024)]
    overlap_try = [0.9, 0.5, 0.75]
    brange_try = [8, 16]
    # Grid Search for FFT parameters
    grid_search(nfft_try, overlap_try, brange_try)

    run_final_model()
