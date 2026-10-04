from datetime import date
from app.extension import db
from app.blueprints.auth.modules import Credential


class Friendship(db.Model):
    __tablename__ = "friendship"

    fid = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("credential.pid"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("credential.pid"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=date.today, nullable=False)
    responded_at = db.Column(db.DateTime, nullable=True)

    sender = db.relationship(
        "Credential",
        foreign_keys=[sender_id],
        backref=db.backref("sent_friend_requests", lazy="dynamic")
    )

    receiver = db.relationship(
        "Credential",
        foreign_keys=[receiver_id],
        backref=db.backref("received_friend_requests", lazy="dynamic")
    )

    __table_args__ = (
        db.UniqueConstraint(
            "sender_id",
            "receiver_id",
            name="unique_friend_request"
        ),
        db.CheckConstraint(
            "sender_id != receiver_id",
            name="check_no_self_friendship"
        ),
    )

    def __repr__(self):
        return f"<Friendship {self.sender_id} -> {self.receiver_id} ({self.status})>"