# Animals-10-Deployment

This project aims to build an multiclass image classification model, deployed in TF-Lite format.

The data is acquired from [kaggle](https://www.kaggle.com/), do refer to it [here](https://www.kaggle.com/datasets/alessiocorrado99/animals10).
![Cute Cat](Animals-10%20dataset%20preview.png?raw=true "Animals-10")

This project implements Transfer Learning using the InceptionV3model, added with custom Conv2D MaxPool layers. 
![Cute Cat](InceptionV3%20Architecture.png?raw=true "Inception V3 Architecture")
src : [incV3](https://paperswithcode.com/method/inception-v3)

InceptionV3 is a 42 layer deep CNN model developed by Google. 
Also known as GoogLeNet, this model has a high image classification performance, utilizing convolution, average pool, max pool, concat, dropout, fully connected and softmax layers.
