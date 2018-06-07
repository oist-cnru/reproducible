"""A simple code producing and saving some results"""
import random
import pickle


def walk(n):
    """A simple random walk generator"""
    steps = [0]
    for i in range(n):
        steps.append(steps[-1] + random.choice([-1, 1]))
    return steps


if __name__ == '__main__':
    random.seed(1)
    results = walk(10)
    with open('results.pickle', 'wb') as f:
        pickle.dump(results, f)
