class Team:
    def __init__(self, id, speed, membros=4): # Definisci 4 componenti di default
        self.id = id
        self.speed = speed
        self.membri = membros # Numero di persone nel team
        self.available = True
        self.distance_travelled = 0
        self.busy_time = 0
        self.completed_jobs = 0

    def finish_job(self):
        self.completed_jobs += 1