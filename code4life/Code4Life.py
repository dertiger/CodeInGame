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
        self.expertise_gain_value = 0

    def get_expertise_gain_in_array(self):
        expertise_gain_array = np.zeros(5, dtype=int)
        if 0 <= self.expertise_gain <= 4:
            expertise_gain_array[self.expertise_gain] = 1
        return expertise_gain_array

    def calc_expertise_gain_value(self, samples_to_check, expertise):
        self.expertise_gain_value = 0
        for sample in samples_to_check:
            if self != sample:
                if 0 <= self.expertise_gain <= 4:
                    if sample.cost[self.expertise_gain] - expertise[self.expertise_gain] > 0:
                        self.expertise_gain_value += 1


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

    def get_carrying_samples_sorted(self):
        carrying_samples = self.get_carrying_samples()
        print("unsorted: ", file=sys.stderr)
        for carrying_sample in carrying_samples:
            print(carrying_sample.sample_id, file=sys.stderr)
            carrying_sample.calc_expertise_gain_value(carrying_samples, self.expertise)
        sorted_carrying_samples = sorted(carrying_samples, key=lambda sample: sample.expertise_gain_value, reverse=True)
        print("sorted: ", file=sys.stderr)
        for carrying_sample in sorted_carrying_samples:
            print(carrying_sample.sample_id, file=sys.stderr)
        return sorted_carrying_samples

    def check_available_storage(self, player_sample: Sample) -> bool:
        effective_cost = self.get_private_cost_of_sample(player_sample)
        for index, type in range(5):
            if effective_cost[type] > self.storage[type]:
                return False
        return True

    def get_private_cost_of_sample(self, sample: Sample, additional_expertise=[0, 0, 0, 0, 0]) -> list:
        effective_costs = []
        for index in range(5):
            effective_cost = sample.cost[index] - self.expertise[index] - additional_expertise[index]
            if effective_cost < 0:
                effective_costs.append(0)
            else:
                effective_costs.append(effective_cost)
        return effective_costs

    def check_insufficient_resources(self, sample: Sample):
        for i in range(5):
            if sample.cost[i] > (available[i] + self.expertise[i]):
                return True
        return False

    def storage_full(self) -> bool:
        if sum(self.storage) == 10:
            return True
        return False

    def all_molecules_for_sample(self, sample: Sample):
        cost = self.get_private_cost_of_sample(sample)
        for index in range(5):
            if cost[index] > self.storage[index]:
                return False
        return True

    def all_molecules_for_samples(self):
        carrying_samples = self.get_carrying_samples_sorted()
        costs = np.zeros(5, dtype=int)
        additional_expertise = np.zeros(5, dtype=int)
        for carrying_sample in carrying_samples:
            costs += self.get_private_cost_of_sample(carrying_sample, additional_expertise)
            additional_expertise += carrying_sample.get_expertise_gain_in_array()
        for index in range(5):
            if costs[index] > self.storage[index]:
                return False
        return True


players = [Player(0), Player(1)]
samples = []
available = []


class Statemachine:
    @staticmethod
    def state_machine() -> str:
        if players[0].eta > 0:
            return Statemachine.state_wait()
        elif players[0].target == "DIAGNOSIS":
            return Statemachine.state_diagnosis()
        elif players[0].target == "MOLECULES":
            return Statemachine.state_molecules()
        elif players[0].target == "LABORATORY":
            return Statemachine.state_laboratory()
        elif players[0].target == "SAMPLES":
            return Statemachine.state_samples()
        else:
            return Statemachine.state_init_state()

    @staticmethod
    def state_init_state() -> str:
        return "GOTO SAMPLES"

    @staticmethod
    def state_wait() -> str:
        return "WAIT"

    @staticmethod
    def state_samples() -> str:
        player_samples = players[0].get_carrying_samples()
        if len(player_samples) < 3:
            if sum(players[0].expertise) < 5:
                return "CONNECT 1"  # TODO: connect to coresponding lvl
            else:
                return "CONNECT 2"
        else:
            return "GOTO DIAGNOSIS"

    @staticmethod
    def state_diagnosis() -> str:
        player_samples = players[0].get_carrying_samples_sorted()
        unidentified_player_sample = [unidentified_player_sample for unidentified_player_sample in player_samples if
                                      not unidentified_player_sample.identified]
        if len(unidentified_player_sample) > 0:
            unidentified_player_sample[0].identified = True
            return "CONNECT " + str(unidentified_player_sample[0].sample_id)
        else:
            samples_with_insufficient_resources = [sample for sample in player_samples if
                                                   players[0].check_insufficient_resources(sample)]
            samples_with_insufficient_resources = np.asarray(samples_with_insufficient_resources)
            if samples_with_insufficient_resources.any():
                print(samples_with_insufficient_resources[0].cost, file=sys.stderr)
                return "CONNECT " + str(samples_with_insufficient_resources[0].sample_id)
            elif len(player_samples) == 0:
                return "GOTO SAMPLES"
            else:
                return "GOTO MOLECULES"
        # TODO: get cloud infos :D / get samples with sufficient resources
        # aviable_ids = [all_samples.sample_id for all_samples in samples if all_samples.carried_by is -1]
        # answer = "CONNECT " + str(aviable_ids[0])

    @staticmethod
    def state_molecules() -> str:
        player_samples = players[0].get_carrying_samples_sorted()
        if players[0].storage_full() or players[0].all_molecules_for_samples():
            return "GOTO LABORATORY"
        else:
            costs = np.zeros(5, dtype=int)
            additional_expertise = np.zeros(5, dtype=int)
            for sample in player_samples:
                costs += players[0].get_private_cost_of_sample(sample, additional_expertise)
                additional_expertise += sample.get_expertise_gain_in_array()
                for index in range(5):
                    if costs[index] > players[0].storage[index]:
                        if available[index] > 0:
                            return "CONNECT " + str(chr(65+index))
        return "GOTO LABORATORY"

    @staticmethod
    def state_laboratory() -> str:
        player_samples = players[0].get_carrying_samples_sorted()
        player_samples = np.asarray(player_samples)
        if not player_samples.any():
            return "GOTO SAMPLES"
        else:
            for player_sample in player_samples:
                if players[0].all_molecules_for_sample(player_sample):
                    return "CONNECT " + str(player_sample.sample_id)
            return "GOTO MOLECULES"


project_count = int(input())
for i in range(project_count):
    a, b, c, d, e = [int(j) for j in input().split()]

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
        new_sample = Sample()
        new_sample.sample_id = int(sample_id)
        new_sample.carried_by = int(carried_by)
        new_sample.rank = int(rank)
        new_sample.expertise_gain = ord(expertise_gain) - 65
        new_sample.health = int(health)
        new_sample.cost = [int(cost_a), int(cost_b), int(cost_c), int(cost_d), int(cost_e)]
        old_sample = [old_sample for old_sample in samples if old_sample.sample_id == new_sample.sample_id]
        old_sample = np.asarray(old_sample)
        if old_sample.any():
            new_sample.identified = old_sample[0].identified  # TODO: identified list
        if new_sample.carried_by == -1:
            new_sample.identified = True
        new_samples.append(new_sample)
    samples.clear()
    samples = new_samples.copy()

    answer = Statemachine.state_machine()

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    print(answer)
