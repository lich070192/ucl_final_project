import gym
from gym.spaces import Discrete, Dict, Box
import numpy as np
import random


class LifecycleEnv(gym.Env):
    def __init__(self, consumption_shock=1):
        # Set starting variables
        self.wealth = 0.1
        self.starting_income = 1
        self.income = self.starting_income
        self.starting_age = 60
        self.age = self.starting_age
        self.retirement_age = 65
        self.terminal_age = 70
        self.last_consumption = self.starting_income
        self.consumption_shock = consumption_shock
        self.minimum_consumption = 0.2
        # define market returns
        self.risk_return = 0.05
        self.risk_free_return = 0.01
        # Observation space: age, from starting age to terminal age and wealth, from 0 to infinite wealth
        self.observation_space = Box(np.array([self.starting_age, 0]),
                                     np.array([self.terminal_age, np.inf]),
                                     shape=(2,))
        # Here we define the choices on consumption and equity allocation
        self.action_space = Box(np.array([-1, -1]), np.array([1, 1]))

    def step(self, action):
        done = False
        # Income reduces when you retire
        if self.age >= self.retirement_age:
            self.income = 0
        # transformation
        action_equity_allocation = (action[0] + 1) / 2
        action_consumption = ((action[1] + 1) / 2) * 10
        # Apply action
        portfolio_return = ((self.risk_return * action_equity_allocation) +
                            (self.risk_free_return * (1 - action_equity_allocation)))
        # Here income is added only after the portfolio return
        self.wealth = (1 + portfolio_return) * \
            (self.wealth - action_consumption) + self.income
        reward = action_consumption
        # penalize reward if consumption falls over a certain threshold
        if abs(action_consumption - self.last_consumption) > (self.last_consumption * self.consumption_shock):
            done = True
        if action_consumption < self.minimum_consumption:
            done = True
        # terminal conditions: check if agent is broke or dead
        if self.wealth < 0:
            self.wealth = 0
            reward = 0
            done = True
        #if random.random() > (0.99 ** np.max(self.age - 85, 0)):
        #    done = True
        if self.age == self.terminal_age:
            done = True
            #reward = 0
        self.last_consumption = action_consumption
        info = {"age": self.age,
                "wealth": self.wealth,
                "percent_consumption": (action_consumption / self.wealth),
                "consumption": action_consumption,
                "equity_allocation": action_equity_allocation,
                "port_return": portfolio_return,
                "reward": reward}
        state = np.array([self.age, self.wealth], dtype=np.float32)
        # Time passes (philosophical consideration here)
        self.age += 1
        return state, reward, done, info

    def render(self, mode='human'):
        # no urgent need for this
        pass

    def reset(self):
        # Resetting age and wealth
        self.wealth = 0.1
        self.age = self.starting_age
        self.income = self.starting_income
        self.last_consumption = self.starting_income
        state = np.array([self.age, self.wealth], dtype=np.float32)
        return state
