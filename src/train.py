import os
import argparse
import multiprocessing
import tensorflow as tf
import models
import data
import helpers


if __name__ == '__main__':
    helpers.seed()

    pwd = os.path.realpath(__file__)
    out_dir = os.path.abspath(os.path.join(pwd, '../../out/')) + '/'
    data_dir = os.path.abspath(os.path.join(pwd, '../../data/')) + '/'

    parser = argparse.ArgumentParser()
    parser.add_argument('--tensorboard', type=str, default=out_dir+'tensorboard/')
    parser.add_argument('--log', type=str, default=out_dir+'training_log.csv')
    parser.add_argument('--plots', type=str, default=out_dir+'plots/')
    parser.add_argument('--model', type=str, default=out_dir+'models/best.hdf5')
    parser.add_argument('--images_path', type=str, default=data_dir+'images/')
    parser.add_argument('--labels_path', type=str, default=data_dir+'labels/')
    parser.add_argument('--img_height', type=int, default=224)
    parser.add_argument('--img_width', type=int, default=224)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--optimizer', type=str, default='adam')
    parser.add_argument('--output_activation', type=str, default='relu')
    parser.add_argument('--learning_rate', type=float, default=0.01)
    parser.add_argument('--loss', type=str, default='binary_crossentropy')
    args = parser.parse_args()

    model = models.vgg16(img_height=args.img_height, img_width=args.img_width, output_activation=args.output_activation, loss=args.loss, optimizer=args.optimizer)
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor='val_acc', min_delta=0, patience=0, verbose=0, mode='auto', baseline=None),
        tf.keras.callbacks.LearningRateScheduler(lambda epoch: args.learning_rate*(0.1**int(epoch/10))),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='val_acc', factor=0.2, patience=10, verbose=0, mode='auto', min_delta=0.0001, cooldown=0, min_lr=0.001),
        tf.keras.callbacks.ModelCheckpoint(filepath=args.model, monitor='val_acc', verbose=1, save_best_only=True, save_weights_only=False, mode='auto', period=1),
        tf.keras.callbacks.TensorBoard(log_dir=args.tensorboard, histogram_freq=0, write_graph=True, write_images=True),
        tf.keras.callbacks.CSVLogger(filename=args.log, separator=',', append=False),
    ]

    x_train, y_train, x_validation, y_validation, _, __ = data.load_split_stratified_data(
        images=data.list_pictures(args.images_path),
        labels=data.list_pictures(args.labels_path),
        img_height=args.img_height,
        img_width=args.img_width,
        split=(0.8, 0.1, 0.1)
    )

    model.fit(
        x=x_train,
        y=y_train,
        batch_size=args.batch_size,
        epochs=args.epochs,
        validation_data=(x_validation, y_validation),
        shuffle=True,
        verbose=1,
        callbacks=callbacks,
    )
