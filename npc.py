import random
import time

NAMES = ['Bram', 'Ottilie', 'Fenwick', 'Marla', 'Quill', 'Dorian', 'Tansy', 'Rufus',
         'Isolde', 'Pip', 'Garrick', 'Wren', 'Odalys', 'Hob', 'Celeste']

ROLES = {
    'Guide': ['Need a hand? Break big quests into small ones.', 'Every block starts with a finished quest.'],
    'Merchant': ['Wares for the diligent! Sadly, no coins yet.', 'Business is booming since you got organised.'],
    'Nurse': ['Rest is part of the work. Take a break.', 'You look tired. Finish one more quest, then sleep.'],
    'Angler': ['Caught nothing today. You caught a whole to-do list.', 'The fish are biting, but you have quests.'],
    'Wizard': ['Procrastination is the darkest magic.', 'I foresee a completed quest in your future.'],
    'Dryad': ['This land grows as you do.', 'Plant a tree. Then finish that quest.'],
}

SKIN = [(242, 201, 160), (217, 162, 115), (168, 111, 71), (122, 74, 43)]
HAIR = [(43, 29, 20), (201, 162, 39), (181, 72, 42), (232, 226, 213), (58, 94, 168)]
SHIRT = [(61, 139, 52), (164, 67, 47), (58, 94, 168), (138, 79, 176), (217, 137, 43), (46, 156, 156)]


class Npc:
    def __init__(self, x):
        self.name = random.choice(NAMES)
        self.role = random.choice(list(ROLES.keys()))
        self.skin = random.choice(SKIN)
        self.hair = random.choice(HAIR)
        self.shirt = random.choice(SHIRT)
        self.x = x
        self.y = 0.0
        self.vx = 0.0
        self.dir = 1
        self.wait = 0.0
        self.say = None
        self.say_until = 0.0

    def update(self, dt, solid_fn, w, h):
        fy = int(self.y)
        cx = int(self.x)
        if not solid_fn(cx, fy):
            # falling
            self.y = min(h - 1, self.y + dt * 14)
            ny = int(self.y)
            if solid_fn(cx, ny):
                self.y = ny
            self.vx = 0
            return
        while solid_fn(cx, int(self.y) - 1) and self.y > 3:
            self.y -= 1
        fy = int(self.y)

        self.wait -= dt
        if self.wait <= 0:
            self.wait = 1 + random.random() * 3
            self.vx = 0 if random.random() < 0.35 else random.choice([-1, 1]) * 1.6
            if self.vx:
                self.dir = 1 if self.vx > 0 else -1

        if self.vx:
            nx = self.x + self.vx * dt
            tx = int(nx)
            if solid_fn(tx, fy - 1) or solid_fn(tx, fy - 2):
                # step up a single-block ledge, otherwise turn around
                if solid_fn(tx, fy - 1) and not solid_fn(tx, fy - 2) and not solid_fn(tx, fy - 3) and not solid_fn(cx, fy - 3):
                    self.y = fy - 1
                    self.x = nx
                else:
                    self.vx = -self.vx
                    self.dir = 1 if self.vx > 0 else -1
            else:
                self.x = nx

    def speak(self):
        self.say = random.choice(ROLES[self.role])
        self.say_until = time.time() + 3.5

    def to_dict(self):
        return {"name": self.name, "role": self.role, "skin": list(self.skin),
                "hair": list(self.hair), "shirt": list(self.shirt), "x": self.x, "y": self.y}

    @staticmethod
    def from_dict(d):
        n = Npc(d["x"])
        n.name, n.role = d["name"], d["role"]
        n.skin, n.hair, n.shirt = tuple(d["skin"]), tuple(d["hair"]), tuple(d["shirt"])
        n.y = d["y"]
        return n