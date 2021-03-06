import scipy.misc as scimisc

from tkinter import *
from PIL import Image
from PIL import ImageTk

import MalmoPython
import os
import sys
import time
import random
import json
import numpy as np
import time

import gym
import gym_minecraft

from gym.wrappers import Monitor

class MinecraftWrapper(gym.Wrapper):
    def __init__(self, env, scale=1/12,grid_shape=None):
        gym.Wrapper.__init__(self, env)
        #self.k = k
        #self.frames = deque(maxlen=k)
        #self.observation_space = spaces.Box(0, 255, shape=(h, w, 1))
        self.scale = scale
        newshape = (env.video_height*scale,env.video_width*scale,1) # dimension of 1 for grayscale
        newshape = tuple(map(int,newshape))
        self.grid_shape = grid_shape

        # the pre processor will adjust the observation space therefore we will edit the property of the environment to take the pre processor into accoutn
        self.observation_space = gym.spaces.Box(low=0, high=255,
        shape=newshape)
    def _preprocess(self, rgb_array):
        frame_shape = rgb_array.shape
        frame = np.array(rgb_array)
        gray_frame = np.dot(frame[...,:3],[0.299,0.587,0.114]).reshape((frame_shape[0],frame_shape[1]))
        smaller = scimisc.imresize(gray_frame,self.scale,mode='L').astype('float64')
        #smaller /= 255.0 #uncomment to normalize within the env.step methood however it is memory efficient to store non-float arrays
        smaller = np.expand_dims(smaller,2) # convert to a 3D array of shape (height,width,grayscale)
        return smaller

    def _reset(self):
        obs = self.env.reset()
        obs = self._preprocess(obs)
        return obs
    def _process_reward(self,info):
        if info is None:
            return 0
        elif 'observation' not in info.keys():
            return 0
        elif info['observation'] is None:
            return 0
        elif 'distanceFromdist' in info['observation'].keys():
            return 10/(0.001 + info['observation']['distanceFromdist'])
        else:
            return 0

    def _step(self, action):
        ob, reward, done, info = self.env.step(action)
        ob = self._preprocess(ob)
        reward += self._process_reward(info)
        return ob, reward, done, info

    def _observation(self):
        assert len(self.frames) == self.k
        return np.concatenate(self.frames, axis=2)/255.



