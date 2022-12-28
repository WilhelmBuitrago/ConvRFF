import tensorflow as tf 


def resize(shape=(256,256)):
    def func(img,mask):
        return tf.image.resize(img,shape),tf.image.resize(mask,shape)
    return func


def data_augmentation(img, mask):
    seed = tf.random.uniform(shape=(2,), minval=1, maxval=1000, dtype=tf.int32)
    img = tf.image.stateless_random_flip_left_right(img, seed)
    mask = tf.image.stateless_random_flip_left_right(mask, seed)

    seed = tf.random.uniform(shape=(2,), minval=1, maxval=1000, dtype=tf.int32)
    img =  tf.image.stateless_random_flip_up_down(img, seed)
    mask = tf.image.stateless_random_flip_up_down(mask, seed)
    
    img = tf.keras.layers.RandomRotation(0.17,fill_mode='reflect',
                                         interpolation='bilinear',
                                         seed=seed,
                                         fill_value=0.0)(img)
    mask = tf.keras.layers.RandomRotation(0.17,fill_mode='reflect',
                                         interpolation='bilinear',
                                         seed=seed,
                                         fill_value=0.0)(mask)

    return img, mask


def preporcess_data(data, data_augmantation=False, 
                    return_label_info=False, shape=256):
    if not return_label_info:
        data = data.map(lambda *items: items[:2])
    data = data.map(lambda x,y,*l: (*resize((shape,shape))(x,y),*l))
    data = data.cache()
    if data_augmantation:
        data = data.map(data_augmentation)
    data = data.batch(32).prefetch(tf.data.AUTOTUNE)
    return data



def get_data(dataset_class, seed=42, data_augmantation=True,
                return_label_info=False, shape=256):

    dataset = dataset_class(seed=seed)
    train_data, val_data, test_data = dataset()

    train_data = preporcess_data(train_data, data_augmantation, 
                    return_label_info, shape)

    val_data = preporcess_data(val_data, False, 
                                return_label_info, shape)

    test_data = preporcess_data(test_data, False, 
                                return_label_info, shape)
    return train_data, val_data, test_data