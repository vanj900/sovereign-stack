# Identity Divergence Experiment

## Importing Necessary Libraries
import numpy as np
import matplotlib.pyplot as plt

## Agent Class Definition
class Agent:
    def __init__(self, id):
        self.id = id
        self.position = np.random.rand(2)

    def get_position(self):
        return self.position

## Divergence Testing Function
def compute_divergence(agent1, agent2):
    return np.linalg.norm(agent1.get_position() - agent2.get_position())

## Visualization Function
def visualize_agents(agents):
    plt.figure(figsize=(8, 6))
    for agent in agents:
        plt.scatter(*agent.get_position(), label=f'Agent {agent.id}')
    plt.title('Agent Positions')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.legend()
    plt.grid(True)
    plt.show()

## Main Function to Run the Experiment
if __name__ == '__main__':
    # Create agents
    agents = [Agent(i) for i in range(5)]
    
    # Testing divergence between first two agents
    divergence = compute_divergence(agents[0], agents[1])
    print(f'Divergence between Agent 0 and Agent 1: {divergence}')

    # Visualize agent positions
    visualize_agents(agents)