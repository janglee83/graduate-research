from typing import List, Dict
from ant_colony_interface import AntColonyInterfaceOperation
from ant_colony_attribute import AntColonyAttribute
from helper import get_name_point_base_index, get_index_base_name_point, calculate_sum_each_path_base_ant, calculate_elite_value
from numpy import ndarray


# define const
START_POINT_VALUE = 'start'
FINISH_POINT_VALUE = 'finish'


class AntColonyOperation(AntColonyAttribute, AntColonyInterfaceOperation):
    def __init__(self, population: int, generation: int, local_ro: List, global_ro: List, weight_matrix: ndarray):
        super().__init__(population=population, generation=generation,
                         local_ro=local_ro, global_ro=global_ro, weight_matrix=weight_matrix)

    def calculate_length(self, path: List[str]) -> float:
        total_length: float = 0

        for index, value in enumerate(path):
            if value != FINISH_POINT_VALUE:
                index_start_point: int = get_index_base_name_point(
                    self.get_weight_matrix(), value)
                index_next_point: int = get_index_base_name_point(
                    self.get_weight_matrix(), path[index + 1])
                total_length += self.get_weight_matrix(
                )[index_start_point][index_next_point]

        return total_length

    def get_each_path_length(self, path: List[str]):
        response_data = {}
        for index, value in enumerate(path):
            if value != FINISH_POINT_VALUE:
                index_start_point: int = get_index_base_name_point(
                    self.get_weight_matrix(), value)
                index_next_point: int = get_index_base_name_point(
                    self.get_weight_matrix(), path[index + 1])

                if path[index + 1] == FINISH_POINT_VALUE:
                    key = int(value)
                else: key = int(path[index + 1])
                # key = f"{value}_{path[index + 1]}"
                response_data[key] = self.get_weight_matrix(
                )[index_start_point][index_next_point]

        return response_data

    # def update_pheromone_intensity(self, list_current_gen_path: List[Dict[str, List[str] | float]]) -> None:
    #     for row in range(self.get_pheromone_tao_matrix().shape[0]):
    #         for col in range(self.get_pheromone_tao_matrix().shape[1]):
    #             name_start_point: str = get_name_point_base_index(self.get_weight_matrix(), row)
    #             name_next_point: str = get_name_point_base_index(self.get_weight_matrix(), col)

    #             update_value: float = calculate_sum_each_path_base_ant(list_current_gen_path, name_start_point,
    #                                                                    name_next_point)
    #             calculate_elite_value(list_current_gen_path, name_start_point, name_next_point,
    #                                   self.get_number_elite_ant())
    #             self.set_each_item_pheromone_tao_matrix(row, col, update_value)

    # def update_pheromone_evaporation(self) -> None:
    #     self.set_pheromone_tao_matrix(1 - self.get_ro())

    def get_eta_value(self, start_point: str, end_point: str) -> float:
        index_start_point: int = get_index_base_name_point(
            self.get_weight_matrix(), start_point)
        index_next_point: int = get_index_base_name_point(
            self.get_weight_matrix(), end_point)
        return 1 / float(self.get_weight_matrix()[index_start_point, index_next_point])

    def get_list_available_next_note(self, start_point: str, list_visited_point: List[str]) -> List[str]:
        reachable_point: List[str] = []

        for index, value in enumerate(
                self.get_weight_matrix()[get_index_base_name_point(self.get_weight_matrix(), start_point)]):
            if isinstance(value, (int, float)) and value > 0 and index + 1 != len(self.get_weight_matrix()) and str(
                    index) not in list_visited_point:
                reachable_point.append(str(index))

        return reachable_point

    def calculate_equation_value(self, start_point: str, next_point: str) -> float:
        index_start_point: int = get_index_base_name_point(
            self.get_weight_matrix(), start_point)
        index_next_point: int = get_index_base_name_point(
            self.get_weight_matrix(), next_point)

        return (pow(self.get_pheromone_tao_matrix()[index_start_point][index_next_point], self.get_alpha())
                * pow(self.get_eta_value(start_point, next_point), self.get_beta()))

    def get_best_next_point(self, start_point: str, list_reachable_point: List[str]) -> str:
        if not list_reachable_point:
            return FINISH_POINT_VALUE

        equation_value: Dict[str, float] = {next_point: self.calculate_equation_value(start_point, next_point) for
                                            next_point in list_reachable_point}

        total_equation_value = sum(equation_value.values())

        point: Dict[str, float] = {}

        for item, value in equation_value.items():
            point[item] = value / total_equation_value

        return max(point, key=point.get, default=-1)

    def update_local_pheromone(self) -> None:
        for row in range(self.get_pheromone_tao_matrix().shape[0]):
            for col in range(self.get_pheromone_tao_matrix().shape[1]):
                # name_next_point: str = get_name_point_base_index(
                #     self.get_weight_matrix(), col)
                # print(self.get_local_ro(col))
                update_value: float = ((1 - self.get_local_ro(col)) * float(self.get_pheromone_tao_matrix()[row][col])
                                       + self.get_default_pheromone_tao_matrix()[row][col] * self.get_local_ro(col))
                # print(update_value)
                self.set_assign_value_pheromone_tao_matrix(
                    row, col, update_value)

    def update_global_pheromone(self, best_current_gen_path: Dict[str, List[str] | float]) -> None:
        for row in range(self.get_pheromone_tao_matrix().shape[0]):
            for col in range(self.get_pheromone_tao_matrix().shape[1]):
                name_start_point: str = get_name_point_base_index(
                    self.get_weight_matrix(), row)
                name_next_point: str = get_name_point_base_index(
                    self.get_weight_matrix(), col)

                for index, path_item in enumerate(best_current_gen_path['path'][:-1]):
                    if path_item == name_start_point and best_current_gen_path['path'][index + 1] == name_next_point:
                        update_value: float = (1 - self.get_global_ro(col)) * float(self.get_pheromone_tao_matrix()[
                            row][col]) + self.get_global_ro(col) * (1 / best_current_gen_path['length'])

                        self.set_assign_value_pheromone_tao_matrix(
                            row, col, update_value)
