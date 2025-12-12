# This file contains the options that you should modify to solve Question 2


def question2_1():
    # TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,  # to make the environment deterministic as the agent should prefer the longer path without any risk
        "discount_factor": 1,  # to ensure that future rewards are not discounted and the agent considers all future rewards equally
        "living_reward": -5,  # to encourage the agent to reach the terminal state quickly
    }


def question2_2():
    # TODO: Choose options that would lead to the desired results
    return {
        "noise": 0.2,  # to introduce some uncertainty in the environment so that the agent avoids the risky longer path
        "discount_factor": 0.5,  # to make the agent prefer near future rewards over distant future rewards
        "living_reward": -1,  # to encourage the agent to reach the terminal state quickly but not too aggressively
    }


def question2_3():
    # TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,  # to make the environment deterministic as the agent should prefer the longer path without any risk
        "discount_factor": 1,  # to ensure that future rewards are not discounted and the agent considers all future rewards equally
        "living_reward": -1,  # to encourage the agent to reach the terminal state quickly
    }


def question2_4():
    # TODO: Choose options that would lead to the desired results
    return {
        "noise": 0.2,  # to introduce some uncertainty in the environment so that the agent avoids the risky longer path
        "discount_factor": 1,  # to ensure that future rewards are not discounted and the agent considers all future rewards equally
        # to slightly encourage the agent to reach the terminal state quickly without being too aggressive as it might take risks which we need to avoid
        "living_reward": -0.1,
    }


def question2_5():
    # TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,  # to make the environment deterministic as the agent should prefer the longer path without any risk
        "discount_factor": 1,  # to ensure that future rewards are not discounted and the agent considers all future rewards equally
        "living_reward": 5,  # to encourage the agent to avoid both terminal states and keep living, it would iterate indefinitely
    }


def question2_6():
    # TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,  # to make the environment deterministic as the agent should prefer the longer path without any risk
        "discount_factor": 1,  # to ensure that future rewards are not discounted and the agent considers all future rewards equally
        "living_reward": -100,  # to strongly encourage the agent to reach the terminal state quickly
    }
