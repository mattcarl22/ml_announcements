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
    if not os.path.isdir(model.name):
        os.mkdir(model.name)

    mc = ModelCheckpoint(os.path.join(model.name, 'best_model.h5'), save_best_only=True, monitor='val_loss', mode='min', verbose=0) # TODO: change verbose to 0 after testing
    kwargs['callbacks'] = [mc]
    history = model.fit(**kwargs)
    model.load_weights(os.path.join(model.name, 'best_model.h5'))
    model.save(model.name)

    return model, history

def build_network(features=32, ffn_node_sizes=[64, 64], dropout=0.05, name="ffn_net", activation_='relu'):
    firm_input = Input(shape=(32), name='firm-specific')
    model_inputs = [firm_input]
    w = Dense(ffn_node_sizes[0], activation=activation_)(firm_input)
    w = Dropout(dropout)(w) 
    for size in ffn_node_sizes[1:]:
        w = Dense(size, activation=activation_)(w)
        w = Dropout(dropout)(w)
    w = Dense(1)(w)
    model = Model(inputs=model_inputs, outputs=w, name=name)
    model.summary()
    tf.keras.utils.plot_model(model, to_file='{0}.png'.format(name), show_shapes=True, show_layer_names=True)

    return model

def compile_network(model, optimizer_='adam', loss_='MSE', batch_size_=32, learning_rate_=0.001, run_eagerly=False):
    optimizer_ = optimizer[optimizer_](learning_rate=learning_rate_)
    model.compile(optimizer=optimizer_, loss=loss_, run_eagerly=run_eagerly)

    return model

def load_data(split_weights = [0.6, 0.8]):
    ### Read data
    # path = "/Users/matthewcarl/Dropbox/research/ml_announcements/"
    # os.chdir(path)

    data = pd.read_excel('../data/final/macro_financial_announcement_data.xlsx',engine='openpyxl')

    # Keep relevant dates
    data = data[(data['weekend'] == 0) & (data['Date'] >= '1990-01-01') & (data['Date'] < '2020-01-01')]
    data = data.reset_index(drop=True)

    ### Keep relevant variables for analysis
    vars = pd.read_excel('../data/final/varlist.xlsx',engine='openpyxl')

    # The first column is the announcement variable; all subsequent columns are the features
    var_list = [vars['Announcement Indicator'][0]]+list(vars['Main variables to include'].dropna())

    data = data[var_list]

    ### Fix missing data
    # USD-EUR exchange rate
    data['exchg_useur_d']=data['exchg_useur_d'].fillna(0)

    # Fill other missing data with previous observation (for now) and drop other missing rows
    data = data.ffill()
    data = data.dropna()


    y_data = data['FOMC'].to_numpy().reshape((-1, 1))
    x_data = data.loc[:, data.columns != 'FOMC'].to_numpy()
    split_vals = [int(data.shape[0] * split_weights[0]), int(data.shape[0] * split_weights[1])]
    reshape = lambda data: data.reshape(data.shape[0], data.shape[1], 1)
    x_train, x_validation, x_test = np.split(x_data, split_vals)
    y_train, y_validation, y_test = list(map(reshape, np.split(y_data, split_vals)))

    print(y_train.shape)
    print(x_train.shape)

    return {
        'x_train': x_train,
        'x_validation': x_validation,
        'x_test': x_test,
        'y_train': y_train,
        'y_validation': y_validation,
        'y_test': y_test
    }

def announcement_ffn(model_name='ffn_test', loss_='MSE', learning_rate_=0.0005, epochs=100):
    data = load_data()
    print('Shape: {0}'.format(data['x_train'].shape[0]))
    model = build_network(
        features = data['x_train'].shape[0],
        ffn_node_sizes=[64, 64],
        name=model_name
    )
    
    compile_network(model, run_eagerly=True, loss_=loss_, learning_rate_=learning_rate_)

    model, history = train(
        x=data['x_train'],
        y=data['y_train'],
        validation_data=(data['x_validation'], data['y_validation']),
        # validation steps ? 
        epochs=epochs, verbose=1,
        model = model
    )

    test_loss = model.evaluate(data['x_test'], data['y_test'])
    fig = plt.figure(figsize=(12,6))
    plt.title('Simulation 1 loss')
    plt.plot(history.history['loss'], label="Out-of-sample loss: {0}".format(test_loss))
    plt.legend(loc="upper right")
    plt.savefig('{0}_loss.png'.format(model_name))

    return model, test_loss

announcement_ffn(loss_='MSE', learning_rate_=0.0005, epochs=100)
