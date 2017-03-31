
from scipy import *
import pylab
import copy
import math
import numpy as np
import random
from Environment import Environment
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class PMEnv(Environment):

  def __init__(self, name = None, numberOfAssets = 100, maxEpisodeLength = 10000):
    self.numberOfAssets = numberOfAssets
    self.initialiseAssetHealths()
    self.assetHealthDecreaseRate = np.zeros(self.numberOfAssets)
    self.maintenanceCost = 0.0
    self.count = 0
    self.maxEpisodeLength = maxEpisodeLength
    self.done = False
    self.fig = plt.figure()
    self.latestAction = None

  def initialiseAssetHealths(self):
    self.assetHealths = np.zeros(self.numberOfAssets)
    for i in range(len(self.assetHealths)):
      self.assetHealths[i] = random.uniform(0.9, 1.0)

  def getState(self):
    return self.assetHealths

  def getActionSize(self):
    return self.numberOfAssets + 1

  def update(self, action):
    self.latestAction = action
    self.count = self.count + 1
    self.maintenanceCost = 0.0
    for i in range(len(self.assetHealths)):
      if i == action:        
        self.assetHealths[i] = min(1.0, self.assetHealths[i] + random.uniform(0.5,1.0))
        self.assetHealthDecreaseRate[i] = 0.0
        self.maintenanceCost = 3.0
      else:
        if self.assetHealthDecreaseRate[i] == 0.0:
          if random.uniform(0,1) < 0.005:
            self.assetHealthDecreaseRate[i] = random.uniform(0.001,0.2)
        else:
          self.assetHealthDecreaseRate[i] += random.uniform(-0.03, 0.1)
        self.assetHealths[i] = max(0.0, self.assetHealths[i] - self.assetHealthDecreaseRate[i])

  def getPossibleActions(self):
    possibleActions = range(self.numberOfAssets + 1)
    return possibleActions

  def getReward(self):
    reward = 0
    for health in self.assetHealths:
      if health < 0.75:
        reward = -1 * math.exp(3*(0.75-health))
    reward = reward - self.maintenanceCost 
    return reward

  def checkTerminal(self):
    if self.count >= self.maxEpisodeLength:
      return True
    else:
      return False

  def reset(self):
    self.__init__(numberOfAssets = self.numberOfAssets, maxEpisodeLength = self.maxEpisodeLength)

  def render(self):
    if self.count % 1 == 0:
      self.fig.clear()
      ax = self.fig.add_subplot(111)
      ax.bar(range(self.numberOfAssets), self.assetHealths)
      if self.latestAction is not None:
        if self.latestAction < self.numberOfAssets:
          ax.bar(self.latestAction,-0.2, color='red')
      ax.set_ylim([-0.2,1])
      ax.set_xlim([0,self.numberOfAssets+1])
      ax.figure.canvas.draw()
      self.fig.show()
    if self.checkTerminal():
      plt.close(self.fig)
      self.fig = plt.figure()

