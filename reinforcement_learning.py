from d3rlpy.datasets import get_cartpole
from d3rlpy.algos import DiscreteCQL
from d3rlpy.metrics.scorer import discounted_sum_of_advantage_scorer
from d3rlpy.metrics.scorer import evaluate_on_environment
from d3rlpy.metrics.scorer import td_error_scorer
from d3rlpy.metrics.scorer import average_value_estimation_scorer
from sklearn.model_selection import train_test_split


# setup CQL algorithm
cql = DiscreteCQL(use_gpu=False)

# split train and test episodes
train_episodes, test_episodes = train_test_split(dataset, test_size=0.2)

# start training
cql.fit(train_episodes,
eval_episodes=test_episodes,
n_epochs=1,
scorers={
    'environment': evaluate_on_environment(env), # evaluate with CartPol-v0 environment
    'advantage': discounted_sum_of_advantage_scorer, # smaller is better
    'td_error': td_error_scorer, # smaller is better
    'value_scale': average_value_estimation_scorer # smaller is better
})