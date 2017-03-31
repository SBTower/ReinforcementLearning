
from scipy import *
import pylab
import copy
import math
import numpy as np
import random
from Vehicles.SimpleVehicle import SimpleVehicle
from Environment import Environment
import shapely.geometry
from shapely.geometry import Point
from shapely.geometry import LineString

import matplotlib.pyplot as plt
import matplotlib.patches as patches

class AVEnvironment(Environment):

  def __init__(self, name = None, width = 200, height = 200):
    self.width = width
    self.height = height
    pos_x = self.width/10 + random.random()*4*self.width/5
    pos_y = self.height/10 + random.random()*4*self.height/5
    orien = random.random()*2*math.pi
    self.boat = SimpleVehicle([pos_x, pos_y, orien])
    self.createBarriers()
    self.createGoal()
    self.done = False
    #self.fig = plt.figure()
    self.count = 0
    self.timestep = 0
    self.maxTimeStep = 100

  def createBarriers(self):
    barrier1 = [[0, 5], [self.width, 5], [self.width, 0], [0, 0]]
    barrier2 = [[0, self.height-5], [self.width, self.height-5], [self.width, self.height], [0, self.height]]
    barrier3 = [[self.width-5, self.height], [self.width, self.height], [self.width, 0], [self.width-5, 0]]
    barrier4 = [[5, self.height], [0, self.height], [0, 0], [5, 0]]

    self.barriers = [barrier1, barrier2, barrier3, barrier4]
    #self.barriers = []

  def getState(self):
    sensorLocations = np.array(self.boat.outline)
    sensorReadings = []
    for i in range(len(sensorLocations)):

      if i == 0:
        sign_1 = -1
        sign_2 = 1
        sign_3 = -1
        sign_4 = -1
      elif i == 1:
        sign_1 = -1
        sign_2 = 1
        sign_3 = 1
        sign_4 = 1
      elif i == 2:
        sign_1 = 1
        sign_2 = -1
        sign_3 = 1
        sign_4 = 1
      elif i == 3:
        sign_1 = 1
        sign_2 = -1
        sign_3 = -1
        sing_4 = -1

      sensorReadings.append(self.boat.sensorRange)
      sensorReadings.append(self.boat.sensorRange)
      x1 = sensorLocations[i][0]
      y1 = sensorLocations[i][1]

      for barrier in self.barriers:

        x2 = x1 + sign_1 * self.boat.sensorRange * math.cos(self.boat.pos[2])
        y2 = y1 + sign_2 * self.boat.sensorRange * math.sin(self.boat.pos[2])

        x3 = x1 + sign_3 * self.boat.sensorRange * math.sin(self.boat.pos[2])
        y3 = y1 + sign_4 * self.boat.sensorRange * math.cos(self.boat.pos[2])

        line1 = shapely.geometry.LineString([[x1, y1], [x2, y2]])
        line2 = shapely.geometry.LineString([[x1, y1], [x3, y3]])

        barrierPoly = shapely.geometry.Polygon(np.array(barrier))
        sd = self.boat.sensorRange
        while line1.intersects(barrierPoly) and sd > 0:
          sd = sd - 1
          x2 = x1 + sign_1 * sd * math.cos(self.boat.pos[2])
          y2 = y1 + sign_2 * sd * math.sin(self.boat.pos[2])
          line1 = shapely.geometry.LineString([[x1, y1], [x2, y2]])
        if sd < sensorReadings[2*i]:
          sensorReadings[2*i] = sd

        sd = self.boat.sensorRange
        while line2.intersects(barrierPoly) and sd > 0:
          sd = sd - 1
          x3 = x1 + sign_3 * sd * math.sin(self.boat.pos[2])
          y3 = y1 + sign_4 * sd * math.cos(self.boat.pos[2])
          line2 = shapely.geometry.LineString([[x1, y1], [x3, y3]])
        if sd < sensorReadings[2*i + 1]:
          sensorReadings[2*i + 1] = sd

    #sensorReadings.append(copy.copy(self.boat.pos[0]))
    #sensorReadings.append(copy.copy(self.boat.pos[1]))
    sensorReadings.append(copy.copy(self.boat.speed))
    sensorReadings.append(copy.copy(self.boat.angularVelocity))
    sensorReadings.append(self.getDistanceToGoal())
    sensorReadings.append(self.getAngleToGoal())

    return sensorReadings    

  def createGoal(self):
    goal_x = self.width/10 + random.random()*4*self.width/5
    goal_y = self.height/10 + random.random()*4*self.height/5
    self.goal = [goal_x, goal_y]

  def getDistanceToGoal(self):
    dist_x = self.goal[0] - self.boat.pos[0]
    dist_y = self.goal[1] - self.boat.pos[1]
    distance = math.sqrt(dist_x*dist_x + dist_y*dist_y)
    return distance

  def getAngleToGoal(self):
    dist_x = self.goal[0] - self.boat.pos[0]
    dist_y = self.goal[1] - self.boat.pos[1]

    if dist_y == 0:
      if dist_x == 0:
        angleToGoal = 0
      elif dist_x > 0:
        angleToGoal = math.pi/2
      else:
        angleToGoal = 3*math.pi/2
    elif dist_y > 0:
      if dist_x >= 0:
        angleToGoal = math.atan(abs(dist_x)/abs(dist_y))
      else:
        angleToGoal = 2*math.pi - math.atan(abs(dist_x)/abs(dist_y))
    else:
      if dist_x >= 0:
        angleToGoal = math.pi - math.atan(abs(dist_x)/abs(dist_y))
      else:
        angleToGoal = math.pi + math.atan(abs(dist_x)/abs(dist_y))
    return angleToGoal

  def update(self, action):
    self.timestep = self.timestep + 1
    n1 = action%11
    n2 = action/11
    action1 = float((n1-5))/2
    action2 = float((n2-5))/200
    timestep = 1
    self.boat.changeAcceleration(action1)
    self.boat.changeAngularAcceleration(action2)
    self.boat.updatePosition(timestep)
    if self.checkTerminal():
      self.done = True
    else:
      self.done = False

  def getPossibleActions(self):
    possibleActions = range(121)
    return possibleActions

  def getReward(self):
    if self.hasCrashed():
      reward = -1000
    elif self.checkInGoal():
      reward = 1000
    else:
      reward = -1
    return reward

  def checkTerminal(self):
    if self.hasCrashed():
      return True
    elif self.checkInGoal():
      return True
    elif self.timestep > self.maxTimeStep:
      return True
    else:
      return False

  def checkInGoal(self):
    inGoal = False
    goalPoly = Point(self.goal[0], self.goal[1]).buffer(10)
    boatPoly = Point(self.boat.pos[0], self.boat.pos[1]).buffer(10)
    if goalPoly.intersects(boatPoly):
      inGoal = True
    return inGoal

  def hasCrashed(self):
    crashed = False
    for i in range(len(self.barriers)):
      barrier = np.array(self.barriers[i])
      boat = np.array(self.boat.outline)
      barrierPoly = shapely.geometry.Polygon(barrier)
      boatPoly = shapely.geometry.Polygon(boat)
      if barrierPoly.intersects(boatPoly):
        crashed = True
    return crashed

  def reset(self):
    self.__init__(self.width, self.height)

  def render(self):
    if self.count < 2:
      self.count = self.count + 1
    else:
      self.count = 0
      self.fig.clear()
      ax = self.fig.add_subplot(111)
      for p in self.barriers:
        ax.add_patch(patches.Polygon(p))
      ax.add_patch(patches.Circle(self.goal, radius = 5, fc='g'))
      ax.add_patch(patches.Polygon(self.boat.outline))
      ax.set_ylim([0,self.height])
      ax.set_xlim([0,self.width])
      ax.figure.canvas.draw()
      self.fig.show()
    if self.checkTerminal():
      plt.close(self.fig)
      self.fig = plt.figure()










