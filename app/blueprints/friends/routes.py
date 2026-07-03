from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app.extension import db
from app.blueprints.auth.modules import Credential
from app.blueprints.book.modules import Userbook
from app.blueprints.friends.modules import Friendship

friends = Blueprint("friends", __name__, template_folder="templates")


def get_friendship_between(user_a, user_b):
    return Friendship.query.filter(
        or_(
            and_(Friendship.sender_id == user_a, Friendship.receiver_id == user_b),
            and_(Friendship.sender_id == user_b, Friendship.receiver_id == user_a),
        )
    ).first()


def get_friend_ids(user_id):
    accepted_rows = Friendship.query.filter(
        Friendship.status == "accepted",
        or_(
            Friendship.sender_id == user_id,
            Friendship.receiver_id == user_id
        )
    ).all()

    friend_ids = []
    for row in accepted_rows:
        if row.sender_id == user_id:
            friend_ids.append(row.receiver_id)
        else:
            friend_ids.append(row.sender_id)
    return friend_ids


@friends.route("/")
@login_required
def friends_list():
    friend_ids = get_friend_ids(current_user.pid)

    friend_users = []
    if friend_ids:
        friend_users = Credential.query.filter(Credential.pid.in_(friend_ids)).order_by(Credential.username.asc()).all()

    return render_template("friends/list.html", friends_list=friend_users)


@friends.route("/search", methods=["GET"])
@login_required
def search_users():
    query = request.args.get("q", "").strip()
    results = []

    if query:
        users = Credential.query.filter(
            Credential.username.ilike(f"%{query}%"),
            Credential.pid != current_user.pid
        ).order_by(Credential.username.asc()).all()

        for user in users:
            friendship = get_friendship_between(current_user.pid, user.pid)

            relation_status = None
            request_direction = None

            if friendship:
                relation_status = friendship.status
                if friendship.sender_id == current_user.pid:
                    request_direction = "sent"
                else:
                    request_direction = "received"

            results.append({
                "user": user,
                "friendship": friendship,
                "relation_status": relation_status,
                "request_direction": request_direction
            })

    return render_template("friends/search.html", query=query, results=results)


@friends.route("/send-request/<int:user_id>", methods=["POST"])
@login_required
def send_request(user_id):
    if user_id == current_user.pid:
        flash("You cannot send a friend request to yourself.", "warning")
        return redirect(url_for("friends.search_users"))

    user = Credential.query.get_or_404(user_id)
    existing = get_friendship_between(current_user.pid, user_id)

    if existing:
        if existing.status == "accepted":
            flash(f"You and {user.username} are already friends.", "warning")
        elif existing.status == "pending":
            flash("A friend request already exists between you two.", "warning")
        else:
            flash("A previous request already exists. Please try another user.", "warning")
        return redirect(url_for("friends.search_users", q=user.username))

    new_request = Friendship(
        sender_id=current_user.pid,
        receiver_id=user_id,
        status="pending"
    )
    db.session.add(new_request)
    db.session.commit()

    flash(f"Friend request sent to {user.username}.", "success")
    return redirect(url_for("friends.search_users", q=user.username))


@friends.route("/requests")
@login_required
def requests_page():
    incoming_requests = Friendship.query.filter_by(
        receiver_id=current_user.pid,
        status="pending"
    ).order_by(Friendship.created_at.desc()).all()

    return render_template("friends/requests.html", incoming_requests=incoming_requests)


@friends.route("/accept/<int:fid>", methods=["POST"])
@login_required
def accept_request(fid):
    friend_request = Friendship.query.filter_by(
        fid=fid,
        receiver_id=current_user.pid,
        status="pending"
    ).first_or_404()

    friend_request.status = "accepted"
    friend_request.responded_at = datetime.utcnow()
    db.session.commit()

    flash(f"You are now friends with {friend_request.sender.username}.", "success")
    return redirect(url_for("friends.requests_page"))


@friends.route("/reject/<int:fid>", methods=["POST"])
@login_required
def reject_request(fid):
    friend_request = Friendship.query.filter_by(
        fid=fid,
        receiver_id=current_user.pid,
        status="pending"
    ).first_or_404()

    friend_request.status = "rejected"
    friend_request.responded_at = datetime.utcnow()
    db.session.commit()

    flash(f"Friend request from {friend_request.sender.username} rejected.", "success")
    return redirect(url_for("friends.requests_page"))


@friends.route("/activity")
@login_required
def activity_feed():
    friend_ids = get_friend_ids(current_user.pid)
    activities = []

    if friend_ids:
        activities = Userbook.query.filter(
            Userbook.pid.in_(friend_ids),
            Userbook.status.in_(["Completed", "Currently Reading"])
        ).order_by(
            Userbook.end_date.desc(),
            Userbook.start_date.desc(),
            Userbook.uid.desc()
        ).all()

    return render_template("friends/activity.html", activities=activities)