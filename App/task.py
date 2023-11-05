class Task:
    def __init__(
        self, id, name, description, timeframe, links, people, points, progress
    ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.timeframe = timeframe
        self.links = links
        self.people = people
        self.points = points
        self.progress = progress

    def serialize(self):
        dict = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "timeframe": self.timeframe,
            "links": self.links,
            "people": self.people,
            "points": self.points,
            "self.progress": self.progress,
        }
        return dict
