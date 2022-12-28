import wandb
from wandb.keras import WandbCallback
from gcpds.image_segmentation.losses import DiceCoeficiente
from gcpds.image_segmentation.metrics import (Jaccard, 
                                              Sensitivity,
                                              Specificity,
                                              DiceCoeficienteMetric
)

from convRFF.data import get_data
import tensorflow as tf 



def get_metrics(model, metrics, dataset_class):
    
    *_, data = get_data(dataset_class, data_augmantation=False,
                                        return_label_info=True)
    data = data.unbatch().batch(1)

    labels = getattr(dataset_class(), "labels_info", None)
    labels = list(labels.keys()) if labels else [None]

    results = {}

    for label in labels:
        if label:
            data = data.filter(lambda x,y,l: l == label)
        for name_metric,metric in metrics.items():
            curr = []
            for x,y,*_ in data:
                y_pred = model(x)
                curr.append(metric().compute(y,y_pred))
            mean = abs(np.mean(curr))
            std = np.std(curr)
            results.setdefault('label',[]).append(label)
            results.setdefault('metric',[]).append(name_metric)
            results.setdefault('mean',[]).append(mean)
            results.setdefault('std',[]).append(std)

    return pd.DataFrame(results) 


def get_compile_parameters():
  return {'loss':DiceCoeficiente(),
          'optimizer':tf.keras.optimizers.Adam(learning_rate=1e-3),
          'metrics':[Jaccard(), 
                     Sensitivity(), 
                     Specificity(),
                     DiceCoeficienteMetric()
                     ]
  }


def get_train_parameters(dataset_class):
    train_data, val_data, test_data = get_data(dataset_class)
    return {'x':train_data,
            'validation_data':val_data,
            'epochs':200,
            'callbacks':[WandbCallback(save_model=True)],
    }


def train(model, dataset_class, run=None):
    train_parameters = get_train_parameters(dataset_class)
    compile_parameters  = get_compile_parameters()
    metrics = compile_parameters['metrics']
    model.compile(**train_parameters)
    model.fit(**compile_parameters)
    df_results = calculate_metrics_table(model, metrics, dataset_class)
    if run:
        table = wandb.Table(dataframe=df_results)
        run.log({"metrics": table})


