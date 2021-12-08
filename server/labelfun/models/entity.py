from sqlalchemy import event
from sqlalchemy.util import symbol

from labelfun.extensions import db
from labelfun.models import TaskType, JobStatus


class Entity(db.Model):
    __tablename__ = 'entity'

    id: int = db.Column(db.Integer, primary_key=True)
    key: str = db.Column(db.String, nullable=False)
    thumb_key: str = db.Column(db.String, nullable=False)
    type: TaskType = db.Column(db.Integer, nullable=False)
    status: JobStatus = db.Column(db.Integer, default=JobStatus.UNLABELED)
    annotation: str = db.Column(db.Text)

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = db.relationship('Task', back_populates='entities')

    frames = db.relationship('Frame', back_populates='entity',
                             cascade="all, delete")


@event.listens_for(Entity.status, 'set')
def update_task_status(target, value, oldvalue, initiator):
    task = target.task
    if oldvalue == value:
        pass
    elif oldvalue == JobStatus.UNLABELED and value == JobStatus.UNREVIEWED:
        task.labeled_count += 1
    elif oldvalue == JobStatus.UNREVIEWED and value == JobStatus.DONE:
        task.reviewed_count += 1
    elif oldvalue == JobStatus.UNREVIEWED and value == JobStatus.UNLABELED:
        task.labeled_count -= 1
    elif oldvalue != symbol('NO_VALUE'):
        raise ValueError(
            'Entity status cannot switch from ' + str(oldvalue) + ' to ' + str(
                value))


class Frame(db.Model):
    __tablename__ = 'frame'

    id: int = db.Column(db.Integer, primary_key=True)
    seq: int = db.Column(db.Integer, nullable=False)
    timestamp: int = db.Column(db.Integer, nullable=False)
    key: str = db.Column(db.String, nullable=False)
    thumb_key: str = db.Column(db.String, nullable=False)
    entity_id: int = db.Column(db.Integer, db.ForeignKey('entity.id'),
                               nullable=False)
    entity = db.relationship('Entity', back_populates='frames')
