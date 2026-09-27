class Quest:
    def __init__(self, text, done=False):
        self.text = text
        self.done = done

    def to_dict(self):
        return {"text": self.text, "done": self.done}

    @staticmethod
    def from_dict(d):
        return Quest(d["text"], d.get("done", False))


class QuestLog:
    """Tracks quests and derives the player's level from how many are complete."""

    def __init__(self, quests=None, bonus=0):
        self.quests = quests or []
        self.bonus = bonus  # extra levels granted outside of quests (e.g. the preview button)

    def add(self, text):
        text = text.strip()
        if text:
            self.quests.append(Quest(text))

    def complete(self, quest):
        quest.done = True

    def remove(self, quest):
        if not quest.done:
            self.quests.remove(quest)

    def completed_count(self):
        return sum(1 for q in self.quests if q.done)

    def level(self):
        return self.completed_count() + self.bonus

    def to_dict(self):
        return {"quests": [q.to_dict() for q in self.quests], "bonus": self.bonus}

    @staticmethod
    def from_dict(d):
        return QuestLog([Quest.from_dict(q) for q in d.get("quests", [])], d.get("bonus", 0))