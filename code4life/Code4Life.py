import sys
import math
import numpy as np

# Bring data on patient samples from the diagnosis machine to the laboratory with enough molecules to produce medicine!


class Sample:
    def __init__(self) -> None:
        super().__init__()
        self.sample_id = 0
        self.carried_by = 0
        self.rank = 0
        self.expertise_gain = 0
        self.health = 0
        self.cost = []
        self.identified = False


class Player:
    def __init__(self, playerNr) -> None:
        super().__init__()
        self.target = ""
        self.score = 0
        self.eta = 0
        self.storage = []
        self.expertise = []
        self.player = playerNr

    def get_carrying_samples(self) -> list:
        return [p_samples for p_samples in samples if p_samples.carried_by == self.player]

    def check_available_storage(self, player_sample: Sample) -> bool:
        effective_cost = self.get_private_cost_of_sample(player_sample)
        for index, type in range(5):
            if effective_cost[type] > self.storage[type]:
                return False
        return True

    def get_private_cost_of_sample(self, player_sample: Sample) -> list:
        effective_costs = []
        for index, i in range(5):
            effective_cost = player_sample.cost[i] - self.expertise[i]
            if effective_cost < 0:
                effective_costs.append(0)
            else:
                effective_costs.append(effective_cost)
        return effective_costs

    def check_insufficient_resources(self, player_sample: Sample, available):
        for i in range(5):
            print("cost resource: " + str(i) + " amount: " + str(player_sample.cost[i]), file=sys.stderr)
            print("aviable  resource: " + str(i) + " amount: " + str(available[i]), file=sys.stderr)
            if player_sample.cost[i] > (available[i] + self.expertise[i]):
                return True
        return False


project_count = int(input())
for i in range(project_count):
    a, b, c, d, e = [int(j) for j in input().split()]

players = [Player(0), Player(1)]
samples = []
available = []

while True:
    for i in range(2):
        target, eta, score, storage_a, storage_b, storage_c, storage_d, storage_e, expertise_a, expertise_b, expertise_c, expertise_d, expertise_e = input().split()
        players[i].target = target
        players[i].eta = int(eta)
        players[i].score = int(score)
        players[i].storage = [int(storage_a), int(storage_b), int(storage_c), int(storage_d), int(storage_e)]
        players[i].expertise = [int(expertise_a), int(expertise_b), int(expertise_c), int(expertise_d), int(expertise_e)]
    available_a, available_b, available_c, available_d, available_e = [int(i) for i in input().split()]
    available = [available_a, available_b, available_c, available_d, available_e]
    sample_count = int(input())
    new_samples = []
    for i in range(sample_count):
        sample_id, carried_by, rank, expertise_gain, health, cost_a, cost_b, cost_c, cost_d, cost_e = input().split()
        sample = Sample()
        sample.sample_id = int(sample_id)
        sample.carried_by = int(carried_by)
        sample.rank = int(rank)
        sample.health = int(health)
        sample.cost = [int(cost_a), int(cost_b), int(cost_c), int(cost_d), int(cost_e)]
        old_sample = [old_sample for old_sample in samples if old_sample.sample_id == sample.sample_id]
        old_sample = np.asarray(old_sample)
        if old_sample.any():
            sample.identified = old_sample[0].identified  # TODO: identified list
        if sample.carried_by == -1:
            sample.identified = True
        new_samples.append(sample)
    samples.clear()
    samples = new_samples.copy()

    answer = ""
    player_samples = players[0].get_carrying_samples()
    if players[0].eta > 0:
        answer = "WAIT"
    elif players[0].target == "DIAGNOSIS":
        unidentified_player_sample = [unidentified_player_sample for unidentified_player_sample in player_samples if not unidentified_player_sample.identified]
        if len(unidentified_player_sample) > 0:
            answer = "CONNECT " + str(unidentified_player_sample[0].sample_id)
            unidentified_player_sample[0].identified = True
        else:
            samples_with_insufficient_resources = [sample for sample in player_samples if players[0].check_insufficient_resources(sample, available)]
            samples_with_insufficient_resources = np.asarray(samples_with_insufficient_resources)
            if samples_with_insufficient_resources.any():
                answer = "CONNECT " + str(samples_with_insufficient_resources[0].sample_id)
            else:
                if len(player_samples) == 0:
                    answer = "GOTO SAMPLES"
                else:
                    answer = "GOTO MOLECULES"
        # TODO: get cloud infos :D
        # aviable_ids = [all_samples.sample_id for all_samples in samples if all_samples.carried_by is -1]
        # answer = "CONNECT " + str(aviable_ids[0])
    elif players[0].target == "MOLECULES":
        needed_molecules = [[player_sample.cost[0]-players[0].expertise[0], player_sample.cost[1]-players[0].expertise[1], player_sample.cost[2]-players[0].expertise[2], player_sample.cost[3]-players[0].expertise[3], player_sample.cost[4]-players[0].expertise[4]] for player_sample in player_samples]
        needed_molecules = [molecule for molecules in needed_molecules for molecule in molecules if molecule >= 0]
        nr_needed_molecules = np.sum(needed_molecules)
        nr_molecules_player = np.sum(players[0].storage)
        if nr_molecules_player == 10 or nr_molecules_player >= nr_needed_molecules:
            answer = "GOTO LABORATORY"
        else:
            for index_recipe, recipe_nr in enumerate(range(len(player_samples))):
                for index_type, molecule_type in enumerate(range(5)):
                    needed_molecules_ofType = np.sum([player_samples[indexes_recipe].cost[index_type]-players[0].expertise[index_type] for indexes_recipe, i in enumerate(range(index_recipe+1))])
                    if needed_molecules_ofType > players[0].storage[index_type]:
                        if answer == "":
                            answer = "CONNECT " + str(chr(65+index_type)) # TODO: break? XD LOLOLOLOLOLOLOLOLOL

    elif players[0].target == "LABORATORY":
        player_samples = np.asarray(player_samples)
        if not player_samples.any():
            answer = "GOTO SAMPLES"
        else:
            next_sample_cost = np.sum([cost - players[0].expertise[index] for index, cost in enumerate(player_samples[0].cost) if (cost - players[0].expertise[index]) > 0])
            if np.sum(players[0].storage) >= next_sample_cost:
                answer = "CONNECT " + str(player_samples[0].sample_id)
            else:
                answer = "GOTO MOLECULES"
    elif players[0].target == "SAMPLES":
        if len(player_samples) < 3:
            answer = "CONNECT 1"  # TODO: connect to coresponding lvl
        else:
            answer = "GOTO DIAGNOSIS"
    else:
        answer = "GOTO SAMPLES"
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    print(answer)
