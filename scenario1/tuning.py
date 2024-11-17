import optuna
from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from stable_baselines3.common.evaluation import evaluate_policy

from env import SumoEnv

def mask_fn(env):
    return env.valid_action_mask()


def optimize_ppo(trial):

    n_steps = trial.suggest_int('n_steps', 2048, 4096)
    gamma = trial.suggest_float('gamma', 0.9, 0.9999, log=True)
    learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-3)

    env = SumoEnv(gui=False, noWarnings=True, traffic=False, mixedConfigs=False, bunched=False, save=None, continuous=False)
    env = ActionMasker(env, mask_fn)

    model = MaskablePPO(MaskableActorCriticPolicy, env, verbose=0, n_steps=n_steps, gamma=gamma, learning_rate=learning_rate)

    model.learn(total_timesteps=35000)

    mean_reward, _ = evaluate_policy(model, env, n_eval_episodes=10, return_episode_rewards=False)

    env.close()

    return mean_reward

study = optuna.create_study(direction='maximize')
study.optimize(optimize_ppo, n_trials=50)

trial = study.best_trial

print('Value: {}'.format(trial.value))

for key, value in trial.params.items():
    print('{}: {}'.format(key, value))