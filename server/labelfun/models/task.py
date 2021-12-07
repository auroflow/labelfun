from datetime import datetime

from labelfun.extensions import db
from labelfun.models import TaskType, JobStatus
from labelfun.models.entity import Entity


class Task(db.Model):
    __tablename__ = 'task'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String, nullable=False)
    time: datetime = db.Column(db.DateTime, nullable=False)
    type: TaskType = db.Column(db.Integer, nullable=False)
    labels: str = db.Column(db.String)  # separated by commas
    published: bool = db.Column(db.Boolean, default=False)
    status: JobStatus = db.Column(db.Integer, nullable=False)
    creator_id: int = db.Column(db.Integer, db.ForeignKey('user.id'),
                                nullable=False)
    labeler_id: int = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviewer_id: int = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', foreign_keys=[creator_id],
                              back_populates='created_tasks')
    labeler = db.relationship('User', foreign_keys=[labeler_id],
                              back_populates='labeled_tasks')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id],
                               back_populates='reviewed_tasks')

    entities = db.relationship('Entity', back_populates='task',
                               cascade='all, delete')
    entities_count: int = db.Column(db.Integer, default=0)
    labeled_count: int = db.Column(db.Integer, default=0)
    reviewed_count: int = db.Column(db.Integer, default=0)

    def __init__(self, labels, **kwargs):
        super(Task, self).__init__(**kwargs)
        if labels is not None and len(labels):
            self.labels = ','.join(labels)

    def get_labeled_count(self):
        return Entity.query.filter(Entity.task_id == self.id,
                                   Entity.status != JobStatus.UNLABELED).count()

    def get_reviewed_count(self):
        return Entity.query.filter(Entity.task_id == self.id,
                                   Entity.status == JobStatus.DONE).count()
