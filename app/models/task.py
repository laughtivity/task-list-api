from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, default=None)
    is_complete = db.Column(db.Boolean, default=False)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.goal_id"))
    goal = db.relationship("Goal", back_populates="tasks")

    @classmethod
    def from_dict(cls, task_data):
        new_task = Task(
            title = task_data["title"],
            description = task_data["description"]
            # completed_at = task_data["completed_at"]
        )
        return new_task
    
    # method that is used on an object - instance of a class 
    # after the object is created an object
    def to_dict(self):
        if self.goal_id:
            return {
            "id":self.task_id,
            "goal_id": self.goal_id,
            "title":self.title,
            "description":self.description,
            "is_complete": self.is_complete
        }

        return {
            "id":self.task_id,
            "title":self.title,
            "description":self.description,
            "is_complete": self.is_complete
        }
