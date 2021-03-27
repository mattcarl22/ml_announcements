import tensorflow as tf
import numpy as np
import pandas as pd
import os
from matplotlib import pyplot as plt

from tensorflow.keras import Sequential
from tensorflow.keras import Input
from tensorflow.keras import Model
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import concatenate
from tensorflow.keras.layers import Lambda
from tensorflow.keras.callbacks import ModelCheckpoint

optimizer = {
    'adadelta': tf.keras.optimizers.Adadelta,
    'adam': tf.keras.optimizers.Adam
}


def train(*args, **kwargs):
    model = kwargs['model']
    del kwargs['model']
    os.makedirs('./models/{0}'.format(model.name), exist_ok=True)
    mc = ModelCheckpoint(os.path.join(model.name, 'best_model.h5'), save_best_only=True, monitor='val_loss', mode='min', verbose=0) # TODO: change verbose to 0 after testing
    kwargs['callbacks'] = [mc]
    history = model.fit(**kwargs)
    model.load_weights(os.path.join(model.name, 'best_model.h5'))
    model.save('./models/' + model.name)

    return model, history

def build_network(features=32, ffn_node_sizes=[64, 64], dropout=0.05, name="ffn_net", activation_='relu'):
    firm_input = Input(shape=(32), name='Input')
    model_inputs = [firm_input]
    if len(ffn_node_sizes) != 0:
        w = Dense(ffn_node_sizes[0], activation=activation_)(firm_input)
        w = Dropout(dropout)(w) 
        for size in ffn_node_sizes[1:]:
            w = Dense(size, activation=activation_)(w)
            w = Dropout(dropout)(w)
        w = Dense(1)(w)
    else:
        w = Dense(1, activation=activation_)(firm_input)

    model = Model(inputs=model_inputs, outputs=w, name=name)
    model.summary()
    tf.keras.utils.plot_model(model, to_file='{0}.png'.format(name), show_shapes=True, show_layer_names=True)

    return model

def compile_network(model, optimizer_='adam', loss_='MSE', batch_size_=32, learning_rate_=0.001, run_eagerly=False):
    optimizer_ = optimizer[optimizer_](learning_rate=learning_rate_)
    model.compile(optimizer=optimizer_, loss=loss_, run_eagerly=run_eagerly)

    return model

def load_data(split_weights = [0.6, 0.8]):
    print('Loading data...')
    data = pd.read_excel('../data/final/data_analysis.xlsx',engine='openpyxl', index_col=0)
    y_data = data['FOMC'].to_numpy().reshape((-1, 1))
    x_data = data.loc[:, data.columns != 'FOMC'].to_numpy()
    split_vals = [int(data.shape[0] * split_weights[0]), int(data.shape[0] * split_weights[1])]
    reshape = lambda data: data.reshape(data.shape[0], data.shape[1], 1)
    x_train, x_validation, x_test = np.split(x_data, split_vals)
    y_train, y_validation, y_test = list(map(reshape, np.split(y_data, split_vals)))
    print('Data ready')
    return {
        'x_train': x_train,
        'x_validation': x_validation,
        'x_test': x_test,
        'y_train': y_train,
        'y_validation': y_validation,
        'y_test': y_test
    }

def plot_predictions(model, data, name):
    plt.figure()
    y_pred = model.predict(data['x_test'])
    plt.title('Data vs Network labebls')
    plt.plot(y_pred, 'r*', label='Network')
    plt.plot(data['y_test'][:,0,0], 'b*', label='Real')
    plt.legend()
    os.makedirs('./predictions', exist_ok=True)
    plt.savefig('./predictions/predictions_{0}.png'.format(name))


def announcement_ffn(data = None, model_name='ffn_test', loss_='MSE', learning_rate_=0.0005, epochs=100, internal_shapes=[64, 64], verbose=0):
    data = data if data else load_data()
    model = build_network(
        features = data['x_train'].shape[0],
        ffn_node_sizes=internal_shapes,
        name=model_name
    )
    
    compile_network(model, run_eagerly=False, loss_=loss_, learning_rate_=learning_rate_)
    model, history = train(
        x=data['x_train'],
        y=data['y_train'],
        validation_data=(data['x_validation'], data['y_validation']),
        # validation steps ? 
        epochs=epochs, verbose=verbose,
        model = model
    )

    test_loss = model.evaluate(data['x_test'], data['y_test'])
    fig = plt.figure(figsize=(12,6))
    plt.title('Simulation 1 loss')
    plt.plot(history.history['loss'], label="Out-of-sample loss: {0}".format(test_loss))
    plt.legend(loc="upper right")
    os.makedirs('./loss', exist_ok=True)
    plt.savefig('./loss/{0}_loss.png'.format(model_name))
    plot_predictions(model, data, model_name)

    return model, test_loss

def load_model(path='ffn_test'):
    model = tf.keras.models.load_model(path, compile=False)
    compile_network(model, run_eagerly=False)

    return model


def get_name(learning_rate, internal_shapes):
    name = ''
    if len(internal_shapes) != 0:
        for shape in internal_shapes:
            name += str(shape) + '-'
    else:
        name += 'empty '

    name = name[0:len(name) - 1] + '_' + str(learning_rate)

    return name

def multi_architecture_training():
    shapes = [
        [],
        [32],
        [32, 32],
        [64],
        [64, 64]
    ]

    learning_rates = [0.1, 0.01, 0.001, 0.0001]

    data = load_data()
    for shape in shapes:
        for lr in learning_rates:
            announcement_ffn(data = data, model_name=get_name(lr, shape), loss_='MSE', learning_rate_=lr, epochs=256, internal_shapes=shape)
        
