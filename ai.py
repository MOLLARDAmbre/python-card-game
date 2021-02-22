from logger import Logger

class AI():
    """
    Describes the behaviour of the opponent
    """
    def __init__(self, objective, opponent_objective):
        self.objective = objective
        self.opponent_objective = opponent_objective

    def play(self, middle_cards, permanents, hand, opponent_permanents, opponent_monsters, achieved, opponent_achieved):
        to_tap = []
        for card in middle_cards:
            if not card.tapped:
                to_tap.append(card)
        to_tap[0].tap()
        if len(to_tap) > 1:
            to_tap[1].tap()
        Logger.get_instance().log_info("AI played their turn")
