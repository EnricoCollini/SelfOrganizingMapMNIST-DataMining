# -*- coding: utf-8 -*-
"""somMNISTconCENTROIDI.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CHmBXlZeDfiNewPnaPoKCorhQl62wQZi

**SOM WITH MNIST DATA**
"""

import matplotlib.pyplot as plt
import numpy as np
import random as ran
import tensorflow as tf
import numpy as np
 
  
  
  
#-------------------------------------------------------------------------------
#                          CLASSE SOM
#-------------------------------------------------------------------------------


class SOM(object):
    _trained = False
 
    def __init__(self, m, n, dim, n_iterations=100, alpha=None, sigma=None):
        #som mxn
        #dim dimensione input
        #alpha = learning rate def=0.3
        #sigma raggio influenza BMU def = 1/2*max(m,n) 
        self._m = m
        self._n = n
        self.indici = []
        self.diffCentroids = []
        self.oldCentroids = []
        self.newCentroids = []
        if alpha is None:
            alpha = 0.3
        else:
            alpha = float(alpha)
        if sigma is None:
            sigma = max(m, n) / 2.0
        else:
            sigma = float(sigma)
        self._n_iterations = abs(int(n_iterations))
 
        #inizializza grafo
        self._graph = tf.Graph()
 
        
        with self._graph.as_default():
 
            
 
            #inizializza random i vettori dei pesi di tutti i neuroni
            #sono salvati come una matrice [m*n, dim] 
            #i neuroni stanno fermi ma i pesi indicano la posizione di questi
            #nello spazio dell'input. Questi si sposteranno in questo nella
            #fase di training
            self._weightage_vects = tf.Variable(tf.random_normal(
                [m*n, dim]))
 
            #matrice bidimensionale [m*n,dim] per la posizione dei neuroni
            self._location_vects = tf.constant(np.array(
                list(self._neuron_locations(m, n))))
 
            #placeholders dei valori
 
            
            self._vect_input = tf.placeholder("float", [dim])
            #Iteration number
            self._iter_input = tf.placeholder("float")
 
            #il bmu è calcolato attraverso la distanza euclidea
            #tra la posizione dello spazio di input dei pesi in questione
            bmu_index = tf.argmin(tf.sqrt(tf.reduce_sum(
                tf.pow(tf.subtract(self._weightage_vects, tf.stack(
                    [self._vect_input for i in range(m*n)])), 2), 1)),
                                  0)
 
            #This will extract the location of the BMU based on the BMU's
            #index
            slice_input = tf.pad(tf.reshape(bmu_index, [1]),
                                 np.array([[0, 1]]))
            bmu_loc = tf.reshape(tf.slice(self._location_vects, slice_input,
                                          tf.constant(np.array([1, 2]))),
                                 [2])
            
 
            #To compute the alpha and sigma values based on iteration
            #number
            learning_rate_op = tf.subtract(1.0, tf.div(self._iter_input,
                                                  self._n_iterations))
            _alpha_op = tf.multiply(alpha, learning_rate_op)
            _sigma_op = tf.multiply(sigma, learning_rate_op)
 
            #Construct the op that will generate a vector with learning
            #rates for all neurons, based on iteration number and location
            #wrt BMU.
            bmu_distance_squares = tf.reduce_sum(tf.pow(tf.subtract(
                self._location_vects, tf.stack(
                    [bmu_loc for i in range(m*n)])), 2), 1)
            neighbourhood_func = tf.exp(tf.negative(tf.div(tf.cast(
                bmu_distance_squares, "float32"), tf.pow(_sigma_op, 2))))
            learning_rate_op = tf.multiply(_alpha_op, neighbourhood_func)
 
            #Finally, the op that will use learning_rate_op to update
            #the weightage vectors of all neurons based on a particular
            #input
            learning_rate_multiplier = tf.stack([tf.tile(tf.slice(
                learning_rate_op, np.array([i]), np.array([1])), [dim])
                                               for i in range(m*n)])
            weightage_delta = tf.multiply(
                learning_rate_multiplier,
                tf.subtract(tf.stack([self._vect_input for i in range(m*n)]),
                       self._weightage_vects))                                         
            new_weightages_op = tf.add(self._weightage_vects,
                                       weightage_delta)
            self._training_op = tf.assign(self._weightage_vects,
                                          new_weightages_op)   
 
            ##INITIALIZE SESSION
            self._sess = tf.Session()
 
            ##INITIALIZE VARIABLES
            init_op = tf.initialize_all_variables()
            self._sess.run(init_op)
 
    def _neuron_locations(self, m, n):
        #ritorna la posizione di tutti i neuroni in 2d
        for i in range(m):
            for j in range(n):
                yield np.array([i, j])
 
    def train(self, input_vects):
        print("training started")
        #questa funzione effettua il training ma il codice non è chiaro
 
        #Training iterations
        result = self.termination_condition() 
  
        iter_no = 0
        while not result:
            #Train with each vector one by one
            result = self.termination_condition()
            index = iter_no + 1;
            print("epoca numero: ", index)
            totinput = len(input_vects)
            
            i=1
            k=1
            for input_vect in input_vects:
                if i == int(totinput/10)*k :
                    print(k*10,"% training completed")
                    k= k+1
                
                self._sess.run(self._training_op,
                               feed_dict={self._vect_input: input_vect,
                                          self._iter_input: iter_no})
                i = i+1
            iter_no = iter_no + 1
             
            
 
            #Store a centroid grid for easy retrieval later on
            centroid_grid = [[] for i in range(self._m)]
            self._weightages = list(self._sess.run(self._weightage_vects))
            self._locations = list(self._sess.run(self._location_vects))
            for i, loc in enumerate(self._locations):
                centroid_grid[loc[0]].append(self._weightages[i])
            self._centroid_grid = centroid_grid
            
            #mi salvo i centroidi per ogni iterazione per poi compararli (diff) 
            prova = []
            for i in range(0,m):
               for j in range(0,n):
                   prova.append(self._centroid_grid[i][j])
            self.diffCentroids.append(prova)
       
        self._trained = True
 
    def get_centroids(self):
        #ritorna la posizone dei centroidi nella griglia 2d della som
        if not self._trained:
            raise ValueError("SOM not trained yet")
        return self._centroid_grid
       
 
    def map_vects(self, input_vects):
        self.indici = []
        #mappa ogni input al neurone vincente nella griglia 2d della som
        if not self._trained:
            raise ValueError("SOM not trained yet")
 
        to_return = []
        for vect in input_vects:
            min_index = min([i for i in range(len(self._weightages))],
                            key=lambda x: np.linalg.norm(vect-
                                                         self._weightages[x]))
            self.indici.append(min_index)
            to_return.append(self._locations[min_index])
        return to_return
      
      
    def numimg_percentroids(self):
        numeri = []
      
        for i in range(0,self._m*self._n):
            numeri.append(0)
            
        for ind in self.indici:
            numeri[ind] = numeri[ind] + 1
          
        return numeri
    
    def termination_condition(self):
        index = len(self.diffCentroids) - 2
        if index >= 0:
          tot = self._m*self._n
          #prendo gli ultimi e penultimi centroidi
          for i in range(0,tot):     
            self.oldCentroids.append(self.diffCentroids[index][i])
            self.newCentroids.append(self.diffCentroids[index + 1][i])
          diff = []
          for i in self.oldCentroids:
            #calcolo la differneza
            dif = [self.euclidean(i, j) for j in self.newCentroids]
            diff.append(dif)
            print("assestamento rimanente: ", 100-np.linalg.norm(diff), "%")
            #se la norma della differenza... 100-105
            if(np.linalg.norm(diff)>99 and np.linalg.norm(diff) <106):
              return True
            else:
              return False
        else:
          return False
        
    def getOldCentroids(self):
      return self.oldCentroids
    def getNewCentroids(self):
      return self.newCentroids
    def getDiffCentroids(self):
      return self.diffCentroids
    
    def euclidean(self,v1, v2):
        return sum((p-q)**2 for p, q in zip(v1, v2)) ** .5
      
    


#-------------------------------------------------------------------------------
#                FUNZIONI DI VISUALIZZAZIONE DEI DIGITS
#-------------------------------------------------------------------------------


def display_digit(num):
    label = y_train[num].argmax(axis=0)
    image = x_train[num].reshape([28,28])
    plt.title('Example: %d  Label: %d' % (num, label))
    plt.imshow(image, cmap=plt.get_cmap('gray_r'))
    plt.show()
    
def display_immagine(questo):
    image = questo.reshape([28,28])
    plt.imshow(image, cmap=plt.get_cmap('gray_r'))
    plt.show
    
    
    

#-------------------------------------------------------------------------------
#                      MNIST DATASET MANAGEMENT
#-------------------------------------------------------------------------------


from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data", one_hot=True)

#funzione per selezionare le immagini e le labels
def train_size(num):
  #:num tutto fino a num (righe) 
  #: tutte le colonne
    x_train = mnist.train.images[:num,:]
    y_train = mnist.train.labels[:num,:]
    return x_train, y_train

#funzione che ritorna immagini per il test con label che gli passi
def test_label(trainIndex, testSize,label):
  x,y = train_size(testSize)
  x = x[trainIndex:testSize,:]
  y = y[trainIndex:testSize,:]
  immagini = []
  for i in range(testSize - trainIndex):
    max = np.amax(y[i])
    for j in range(len(y[i])):
      if y[i][j] == max:  
        if j== label:
          immagini.append(x[i])
  return immagini
      

trainIndex = 5000
testSize = 5500
label = 0
x_train, y_train = train_size(trainIndex)
x_test, y_test = train_size(testSize)
x_test = x_test[trainIndex:testSize,:]; y_test = y_test[trainIndex:testSize,:]

provaimmagini = test_label(trainIndex,testSize,label)




#-------------------------------------------------------------------------------
#                      DISPLAY DIGIT TESTING
#-------------------------------------------------------------------------------
    

#display di un numero random
display_digit(ran.randint(0, x_train.shape[0]))




#-------------------------------------------------------------------------------
#                      SOM INIT, TRAIN & TEST
#-------------------------------------------------------------------------------


#som 4x4, dimensione input (array di dimensione 784=28x28), num di iterazioni
som = SOM(4,3, x_train.shape[1], 100)
m = 4
n = 3

#training
som.train(x_train)
print("training completed")



#mappa ogni input al neurone vincente nella griglia 2d della som
mapped = som.map_vects(x_train)
mappedarr = np.array(mapped)
x1 = mappedarr[:,0]; y1 = mappedarr[:,1]
index = [ np.where(r==1)[0][0] for r in y_train ]
index = list(map(str, index))
numeri = som.numimg_percentroids()
for idx, nm in enumerate(numeri):
  print("centroide numero: ",idx,"ha ",nm,"immagini" )
  

#testing
print("Testing started")
mappedtest = som.map_vects(x_test)
print("Testing completed")

print("label ", label, " testing started" )
mappedtest = som.map_vects(provaimmagini)

numbs = som.numimg_percentroids()
for idx, nm in enumerate(numbs):
  print("centroide numero: ",idx,"ha ",nm,"immagini" )
print("label ", label, " testing ended" )



#-------------------------------------------------------------------------------
#                      CENTROIDS & VISUALIZATION
#-------------------------------------------------------------------------------


#centroidi = array [] [] [784] 
centroidi = som.get_centroids()

mio = []
for i in range(0,m):
  for j in range(0,n):
    mio.append(centroidi[i][j])
    
mappedtest = som.map_vects(mio)
mappedtestarr = np.array(mappedtest)
x5 = mappedtestarr[:,0]
y5 = mappedtestarr[:,1]
plt.figure(figsize=(20,10))
plt.scatter(x5,y5)
for i, m in enumerate(mapped):
    plt.text( m[0], m[1],index[i], ha='center', va='center', 
             bbox=dict(facecolor='white', alpha=0.5, lw=0))
plt.show()