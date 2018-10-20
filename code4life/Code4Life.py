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
        for carrying_sample in carrying_samples:
            carrying_sample.calc_expertise_gain_value(carrying_samples, self.expertise)
        sorted_carrying_samples = sorted(carrying_samples, key=lambda sample: sample.expertise_gain_value, reverse=True)

        return sorted_carrying_samples

    def get_cloud_samples_highest_health_first(self, min_health=0):
        cloud_samples = [cloud_sample for cloud_sample in samples if cloud_sample.carried_by == -1 if cloud_sample.health >= min_health]
        return sorted(cloud_samples, key=lambda sample: sample.health, reverse=True)

    def get_best_cloud_sample(self, base_samples) -> Sample:
        if len(base_samples) < 3:
            cloud_samples = self.get_cloud_samples_highest_health_first()
            my_existing_costs = self.get_private_cost_of_samples(base_samples)
            my_expertise = np.zeros(5,dtype=int)
            for base_sample in base_samples:
                my_expertise += base_sample.get_expertise_gain_in_array()
            for cloud_sample in cloud_samples:
                if not self.check_insufficient_resources(cloud_sample, my_expertise):
                    full_cost = my_existing_costs + self.get_private_cost_of_sample(cloud_sample, my_expertise)
                    if sum(full_cost) <= 10:
                        return cloud_sample
        return None

    def get_best_cloud_sample_for_my_samples(self) -> Sample:
        return self.get_best_cloud_sample(self.get_carrying_samples_sorted())

    def get_private_cost_of_sample(self, sample: Sample, additional_expertise=[0, 0, 0, 0, 0]) -> list:
        effective_costs = []
        for index in range(5):
            effective_cost = sample.cost[index] - self.expertise[index] - additional_expertise[index]
            if effective_cost < 0:
                effective_costs.append(0)
            else:
                effective_costs.append(effective_cost)
        return effective_costs

    def get_private_cost_of_samples(self, samples):
        cost = np.zeros(5, dtype=int)
        additional_expertise = np.zeros(5, dtype=int)
        for sample_sorted in samples:
            cost += self.get_private_cost_of_sample(sample_sorted, additional_expertise)
            additional_expertise += sample_sorted.get_expertise_gain_in_array()
        return cost

    def get_private_cost_of_my_samples(self):
        samples_sorted = self.get_carrying_samples_sorted()
        return self.get_private_cost_of_samples(samples_sorted)

    def check_insufficient_resources(self, sample: Sample, additional_expertise=[0, 0, 0, 0, 0]):
        for i in range(5):
            if sample.cost[i]-self.storage[i] > (available[i] + self.expertise[i] + additional_expertise[i]):
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
            elif sum(players[0].expertise) < 14:
                return "CONNECT 2"
            else:
                return "CONNECT 3"

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
            samples_with_insufficient_resources = []
            additional_expertise = np.zeros(5, dtype=int)
            for sample in player_samples:
                if players[0].check_insufficient_resources(sample, additional_expertise):
                    samples_with_insufficient_resources.append(sample)
                else:
                    additional_expertise += sample.get_expertise_gain_in_array()
            samples_with_insufficient_resources = np.asarray(samples_with_insufficient_resources)
            if samples_with_insufficient_resources.any():
                print(samples_with_insufficient_resources[0].cost, file=sys.stderr)
                return "CONNECT " + str(samples_with_insufficient_resources[0].sample_id)
            elif len(player_samples) == 0:
                return "GOTO SAMPLES"
            elif len(player_samples) < 3:
                print("CHECK CLOUD...", file=sys.stderr)
                best_cloud_sample = players[0].get_best_cloud_sample_for_my_samples()
                if best_cloud_sample is not None:
                    return "CONNECT " + str(best_cloud_sample.sample_id)
                else:
                    return "GOTO MOLECULES"
            else:
                print("MAX samples found", file=sys.stderr)
                return "GOTO MOLECULES"
        # TODO: get cloud infos :D / get samples with sufficient resources
        # aviable_ids = [all_samples.sample_id for all_samples in samples if all_samples.carried_by is -1]
        # answer = "CONNECT " + str(aviable_ids[0])

    @staticmethod
    def state_molecules() -> str:
        player_samples = players[0].get_carrying_samples_sorted()
        if players[0].storage_full() or players[0].all_molecules_for_samples():
            return "GOTO LABORATORY"
        locked_samples = [locked_sample for locked_sample in player_samples if players[0].check_insufficient_resources(locked_sample)]
        if len(locked_samples) >= len(player_samples):
            return "GOTO DIAGNOSIS"
        else:
            costs = np.zeros(5, dtype=int)
            additional_expertise = np.zeros(5, dtype=int)
            for sample in player_samples:
                costs += players[0].get_private_cost_of_sample(sample, additional_expertise)
                if players[0].all_molecules_for_sample(sample):
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
            return Statemachine.check_cloud_or_samples()
        else:
            for player_sample in player_samples:
                if players[0].all_molecules_for_sample(player_sample):
                    return "CONNECT " + str(player_sample.sample_id)
            if len(player_samples) <= 1:
                return Statemachine.check_cloud_or_samples()
            return "GOTO MOLECULES"

    @staticmethod
    def check_cloud_or_samples() -> str:
        player_samples = players[0].get_carrying_samples_sorted()
        cloud_sample = players[0].get_best_cloud_sample_for_my_samples()
        while cloud_sample is not None:
            player_samples.append(cloud_sample)
            cloud_sample = players[0].get_best_cloud_sample(player_samples)
        if len(player_samples) >= 2:
            return "GOTO DIAGNOSIS"
        return "GOTO SAMPLES"

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
