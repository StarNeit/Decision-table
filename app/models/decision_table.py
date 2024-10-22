import csv
from pathlib import Path
from app.models.abstract import AbstractDecisionTable
from app.models.decision_data_holder import DecisionDataHolder
from typing import Any, List, Dict


class DecisionTable(AbstractDecisionTable):
    def __init__(self, inputs: List[str], outputs: List[str], rows: List[Dict[str, Any]]):
        self.inputs = inputs
        self.outputs = outputs
        self.rows = rows

    @staticmethod
    def create_from_csv(filepath: Path) -> "DecisionTable":
        inputs, outputs, rows = [], [], []
        with filepath.open() as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            header = next(reader)

            split_index = header.index("*")
            inputs = header[:split_index]
            outputs = header[split_index + 1 :]

            for row in reader:
                row_conditions = {}
                for i, input_name in enumerate(inputs):
                    row_conditions[input_name] = row[i]
                row_outputs = {outputs[j]: row[split_index + 1 + j] for j in range(len(outputs))}
                rows.append({"conditions": row_conditions, "outputs": row_outputs})

        return DecisionTable(inputs, outputs, rows)

    def evaluate(self, ddh: DecisionDataHolder) -> bool:
        for row in self.rows:
            if self._conditions_met(row["conditions"], ddh):
                self._apply_outputs(row["outputs"], ddh)
                return True
        return False

    def _conditions_met(self, conditions: Dict[str, str], ddh: DecisionDataHolder) -> bool:
        for predictor, condition in conditions.items():
            if not self._evaluate_condition(ddh.get(predictor), condition):
                return False
        return True

    def _evaluate_condition(self, value: Any, condition: str) -> bool:
        # Basic condition parsing
        if condition.startswith("="):
            return value == self._parse_value(condition[1:])
        elif condition.startswith(">"):
            return value > self._parse_value(condition[1:])
        elif condition.startswith(">="):
            return value >= self._parse_value(condition[2:])
        elif condition.startswith("<"):
            return value < self._parse_value(condition[1:])
        elif condition.startswith("<="):
            return value <= self._parse_value(condition[2:])
        return False

    @staticmethod
    def _parse_value(value: str) -> Any:
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    def _apply_outputs(self, outputs: Dict[str, str], ddh: DecisionDataHolder) -> None:
        for output, value in outputs.items():
            ddh[output] = value
