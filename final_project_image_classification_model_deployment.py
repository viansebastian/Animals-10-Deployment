# -*- coding: utf-8 -*-
"""Final Project Image Classification Model Deployment.ipynb

Automatically generated by Colaboratory.

# Final Submission: Image Classification Model Deployment
Vian Sebastian Bromokusumo

> username: vianvian


> email: viansebastianbromokusumo@mail.ugm.ac.id
"""

# Criteria:
# 1. Dataset min 10.000 images                <----->
# 2. Dataset is never used before             <----->
# 3. 20% test set                             <----->
# 4. Sequential                               <----->
# 5. Model EXPLICITLY  uses Conv2D Max Pooling Layer      <----->
# 6. Accuracy min. 92%                        <----->
# 7. Plot training, validation and loss       <----->
# 8. Save in TFLite                           <----->
# 9. Images must have various resolutions     <----->
# 10. Min. classes = 3                        <----->

!nvidia-smi

# import general dependencies
import tensorflow as tf
from tensorflow.keras.layers import Input
import numpy as np
import matplotlib.pyplot as plt
import pathlib

# checking files
import os

base_dir = '/content/drive/MyDrive/Colab Notebooks/Dicoding Machine Learning Intermediate/archive/raw-img'
os.listdir(base_dir)

# showing dataset's images
from PIL import Image

subdirectories = ['elefante', 'cane', 'pecora', 'scoiattolo', 'gatto', 'mucca', 'cavallo', 'gallina', 'ragno', 'farfalla']

fig, axs = plt.subplots(2, 5, figsize=(10, 5))

axs = axs.flatten()


for i, subdirectory in enumerate(subdirectories):

    files = os.listdir(os.path.join(base_dir, subdirectory))

    image_path = os.path.join(base_dir, subdirectory, files[0])

    img = Image.open(image_path)
    axs[i].imshow(img)
    axs[i].axis('off')
    axs[i].set_title(subdirectory.capitalize())
    print(f"Image shape for {subdirectory}: {img.size}")

print(img.size)
plt.tight_layout()
plt.show()

# showing dataset's distribution
import pandas as pd
import seaborn as sns

subdirectories = ['elefante', 'cane', 'pecora', 'scoiattolo', 'gatto', 'mucca', 'cavallo', 'gallina', 'ragno', 'farfalla']
counts = {}


for i, subdirectory in enumerate(subdirectories):

    files = os.listdir(os.path.join(base_dir, subdirectory))
    counts[subdirectory] = len(files)
    print(f"count {subdirectory}: {counts[subdirectory]}")

df_counts = pd.DataFrame(list(counts.items()), columns=['Label', 'Count'])

plt.figure(figsize=(20, 6))
sns.barplot(x='Count', y='Label', data=df_counts, alpha=0.8, palette='pastel')
plt.title('Distribution of Labels in Image Dataset', fontsize=16)
plt.xlabel('Count', fontsize=14)
plt.ylabel('Label', fontsize=14)
plt.suptitle('Image Dataset Label Distribution', fontsize=20)

plt.show()

# image augmentation
from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(
    rescale=1.0/255,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode='nearest',
    validation_split=0.2
)

val_datagen = ImageDataGenerator(
    rescale=1.0/255,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    base_dir,
    target_size = (224,224),
    batch_size = 128,
    class_mode = 'categorical',
    shuffle = True,
    subset = 'training'
)

val_generator = val_datagen.flow_from_directory(
    base_dir,
    target_size = (224,224),
    batch_size = 128,
    class_mode = 'categorical',
    shuffle = True,
    subset = 'validation'
)

# InceptionV3 Model
from tensorflow.keras.applications import InceptionV3

# load InceptionV3 Model
base_model = InceptionV3(weights='imagenet', include_top=False, input_tensor=Input(shape=(224, 224, 3)))

for layer in base_model.layers:
    layer.trainable = False

# last_output = base_model.output

# InceptionV3 Model Architecture
base_model.summary()

# model's architecture
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, Conv2D, MaxPooling2D, BatchNormalization

model = tf.keras.models.Sequential([
    base_model,
    Conv2D(64, (3, 3), activation = 'relu', padding = 'same'),
    MaxPooling2D((2, 2)),
    Conv2D(128, (3, 3), activation = 'relu', padding = 'same'),
    MaxPooling2D((2,2)),
    GlobalAveragePooling2D(),
    Dense(1024, activation = 'relu'),
    BatchNormalization(),
    Dropout(0.2),
    Dense(512, activation = 'relu'),
    Dense(10, activation='softmax')
])

model.summary()

# implementing callbacks
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, LearningRateScheduler

checkpoint_path = "model_checkpoint.h5"
checkpoint = ModelCheckpoint(
    checkpoint_path,
    monitor = 'accuracy',
    save_best_only = True,
    mode = 'max',
    verbose = 1
)

lr_reduction = ReduceLROnPlateau(
    monitor = 'accuracy',
    patience = 3,
    verbose = 1,
    factor = 0.1,
    min_lr = 0.000001
)

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    acc = logs.get('accuracy')
    val_acc = logs.get('val_accuracy')

    if(acc > 0.92 and val_acc > 0.92):
      print("\nReached wanted accuracy so cancelling training!")
      self.model.stop_training = True

earlyStop = myCallback()

# compiling the model
model.compile(
    loss ='categorical_crossentropy',
    optimizer = tf.optimizers.Adam(learning_rate = 0.001),
    metrics = ['accuracy']
)

# configure steps for train and val per epoch
train_steps = round(20948/128)
val_steps = round(5232/128)

print(train_steps)
print(val_steps)

# training the model
hist = model.fit(
    train_generator,
    steps_per_epoch = train_steps,
    epochs = 100,
    validation_data = val_generator,
    validation_steps = val_steps,
    verbose = 1,
    callbacks = [lr_reduction, earlyStop, checkpoint]
)

# plotting accuracy and loss
accuracy = hist.history['accuracy']
validation_accuracy = hist.history['val_accuracy']
loss = hist.history['loss']
validation_loss = hist.history['val_loss']

fig, ax = plt.subplots(nrows = 3, figsize = (15, 10))

ax[0].plot(accuracy, 'r', label='Accuracy')
ax[0].plot(loss, 'b', label='Loss')
ax[0].set_title('Accuracy and Loss')
ax[0].set_xlabel('Epoch')
ax[0].set_ylabel('Value')
ax[0].legend(loc = 0)

ax[1].plot(accuracy, 'r', label='Accuracy')
ax[1].plot(validation_accuracy, 'b', label='Validation Accuracy')
ax[1].set_title('Acc and Val Acc')
ax[1].set_xlabel('Epoch')
ax[1].set_ylabel('Value')
ax[1].legend(loc = 0)

ax[2].plot(loss, 'r', label='Loss')
ax[2].plot(validation_loss, 'b', label='Val Loss')
ax[2].set_title('Loss and Val Loss')
ax[2].set_xlabel('Epoch')
ax[2].set_ylabel('Value')
ax[2].legend(loc = 0)

plt.tight_layout()
plt.show()

# model deployment and export
export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)

converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()

tflite_model_file = pathlib.Path('animals-classification.tflite')
tflite_model_file.write_bytes(tflite_model)
