
from components.rules_engine.src.rules_runners.base_runner import BaseRulesRunner
from ..models.ruleset import RuleSet

class GoRules(BaseRulesRunner):
  def __init__(self):
    pass

  def load_rules_from_json(self, data: dict, ruleset_id: str):
    # TODO: Implement logic to load a JSON into a specific RuleSet
    pass

  def evaluate(self) -> bool:
    # TODO: Implement the rules execution with this rules engine.
    return False
