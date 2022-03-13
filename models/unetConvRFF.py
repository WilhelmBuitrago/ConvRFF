
from tensorflow.keras import layers
from tensorflow.keras import Model
from tensorflow.keras import regularizers

from convRFF import ConvRFF
from functools import partial

DefaultConv2D = partial(layers.Conv2D,
                        kernel_size=3, activation='relu', padding="same")

DefaultPooling = partial(layers.MaxPool2D,
                        pool_size=2)

DefaultConvRFF = partial(ConvRFF,
                        kernel_size=3, padding="SAME",
                         kernel_regularizer = regularizers.l2(1e-4),
                        trainable_scale=True, trainable_W=True,
                         )

def upsample_simple(**kwargs):
    strides = kwargs['strides']
    return layers.UpSampling2D(strides)

upsample = upsample_simple


def get_model(input_shape=(128,128,3),name='UnetConvRFF',**kwargs):

    # Encoder 
    input = layers.Input(shape=input_shape)

    x =  layers.BatchNormalization()(input)
  
    x =  DefaultConv2D(8)(x)
    x =  layers.BatchNormalization()(x)
    x = level_1 = DefaultConv2D(8)(x)
    x =  layers.BatchNormalization()(x)
    x = DefaultPooling()(x) # 128x128 -> 64x64

    x =  DefaultConv2D(16)(x)
    x =  layers.BatchNormalization()(x)
    x = level_2 = DefaultConv2D(16)(x)
    x =  layers.BatchNormalization()(x)
    x = DefaultPooling()(x) # 64x64 -> 32x32


    x =  DefaultConv2D(32)(x)
    x =  layers.BatchNormalization()(x)
    x = level_3 = DefaultConv2D(32)(x)
    x =  layers.BatchNormalization()(x)
    x = DefaultPooling()(x) # 32x32 -> 16x16

    x = DefaultConv2D(64)(x)
    x =  layers.BatchNormalization()(x)
    x = level_4 =  DefaultConv2D(64)(x)
    x =  layers.BatchNormalization()(x)
    x =  DefaultPooling()(x) # 16x16 -> 8x8


    x = DefaultConvRFF(64)(x)


    #Decoder
    x = DefaultConv2D(128)(x)
    x =  layers.BatchNormalization()(x)
    x = DefaultConv2D(128)(x)
    x =  layers.BatchNormalization()(x)

    
    x = upsample(64)(x) # 8x8 -> 16x16
    x = layers.Concatenate()([level_4,x])
    x = DefaultConv2D(64)(x)
    x =  layers.BatchNormalization()(x)
    x = DefaultConv2D(64)(x)
    x =  layers.BatchNormalization()(x)
    
    x = upsample(32)(x) # 16x16 -> 32x32
    x = layers.Concatenate()([level_3,x])
    x = DefaultConv2D(32)(x)
    x =  layers.BatchNormalization()(x)
    x = DefaultConv2D(32)(x)
    x =  layers.BatchNormalization()(x)

    x = upsample(16)(x) # 32x32 -> 64x64
    x = layers.Concatenate()([level_2,x])
    x = DefaultConv2D(16)(x)
    x =  layers.BatchNormalization()(x)
    x = DefaultConv2D(16)(x)
    x =  layers.BatchNormalization()(x)

    x = upsample(8)(x) # 64x64 -> 128x128
    x = layers.Concatenate()([level_1,x])
    x = DefaultConv2D(8)(x)
    x =  layers.BatchNormalization()(x)
    x = DefaultConv2D(8)(x)
    x =  layers.BatchNormalization()(x)

    x = DefaultConv2D(1,kernel_size=(1,1),activation='sigmoid')(x)

    model = Model(input,x)

    return model 



if __name__ == '__main__':
    model = get_model()
    model.summary()