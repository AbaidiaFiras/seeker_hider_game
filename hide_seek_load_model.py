from stable_baselines3 import PPO

from hide_seek_env import hasEnv

env = hasEnv()


model = PPO.load("ppo_hide_seek")  # loading the model 

env.reset()
for i in range(1000):
    action, _state = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
      env.reset()