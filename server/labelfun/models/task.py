from datetime import datetime

from labelfun.extensions import db
from labelfun.models import TaskType, JobStatus


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
    labeled_count: int = db.Column(db.Integer, default=0)
    reviewed_count: int = db.Column(db.Integer, default=0)

    # For video tasks
    interval: int = db.Column(db.Float)

    def __init__(self, labels, **kwargs):
        super(Task, self).__init__(**kwargs)
        if labels is not None and len(labels):
            self.labels = ','.join(labels)


class Entity(db.Model):
    __tablename__ = 'entity'

    id: int = db.Column(db.Integer, primary_key=True)
    path: str = db.Column(db.String, nullable=False)
    key: str = db.Column(db.String, nullable=False)
    thumb_key: str = db.Column(db.String, nullable=False)
    type: TaskType = db.Column(db.Integer, nullable=False)
    status: JobStatus = db.Column(db.Integer, default=JobStatus.UNLABELED)
    annotation: str = db.Column(db.Text)
    uploaded: bool = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = db.relationship('Task', back_populates='entities')
    review: bool = db.Column(db.Boolean, default=False)
    # For video tasks
    frame_count = db.Column(db.Integer)

# class Frame(db.Model):
#     __tablename__ = 'frame'
#
#     id: int = db.Column(db.Integer, primary_key=True)
#     frame_number: int = db.Column(db.Integer, nullable=False)
#     key: str = db.Column(db.String, nullable=True)
#     thumb_key: str = db.Column(db.String, nullable=True)
#     entity_id: int = db.Column(db.Integer, db.ForeignKey('entity.id'),
#                                nullable=False)
#     entity = db.relationship('Entity', back_populates='frames')
