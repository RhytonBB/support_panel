from flask import Blueprint, render_template, redirect, url_for, request, abort, flash
from flask_login import login_required, current_user
from datetime import datetime
from .models import db, SupportRequest, SupportMessage, Worker
import os, uuid

views_bp = Blueprint("views", __name__)

# ... (весь импорт оставляем как есть)

@views_bp.route("/")
@login_required
def index():
    return render_template("index.html")

@views_bp.route("/requests/<status>")
@login_required
def list_requests(status):
    if status not in ["new", "in_progress", "closed"]:
        abort(404)

    if status == "new":
        requests = SupportRequest.query.filter_by(status="new").all()
    elif status == "in_progress":
        requests = SupportRequest.query.filter_by(status="in_progress", operator_id=current_user.id).all()
    else:
        requests = SupportRequest.query.filter_by(status="closed", operator_id=current_user.id).all()

    enriched = []
    for req in requests:
        worker = Worker.query.filter_by(id=req.worker_id).first()
        if worker:
            enriched.append({
                "request": req,
                "full_name": worker.full_name,
                "telegram_nick": worker.telegram_nick,
                "telegram_id": worker.telegram_id
            })

    return render_template("list_requests.html", status=status, requests=enriched)

@views_bp.route("/requests/respond/<int:request_id>", methods=["POST"])
@login_required
def respond_to_request(request_id):
    req = SupportRequest.query.get_or_404(request_id)
    if req.status != "new":
        flash("Обращение уже в работе")
        return redirect(url_for("views.list_requests", status="new"))

    req.status = "in_progress"
    req.operator_id = current_user.id
    req.accepted_at = datetime.utcnow()
    db.session.commit()

    msg = SupportMessage(
        request_id=req.id,
        sender_role="admin",
        text=f"Оператор {current_user.full_name} подключился к вашему обращению."
    )
    db.session.add(msg)
    db.session.commit()

    return redirect(url_for("views.chat", request_id=request_id))

@views_bp.route("/chat/operator/<int:request_id>")
@login_required
def chat(request_id):
    req = SupportRequest.query.get_or_404(request_id)
    if req.operator_id != current_user.id and req.status != "closed":
        abort(403)

    messages = SupportMessage.query.filter_by(request_id=request_id).order_by(SupportMessage.created_at).all()
    worker = Worker.query.get(req.worker_id)
    return render_template("chat.html",
                           request_id=request_id,
                           messages=messages,
                           status=req.status,
                           full_name=worker.full_name,
                           telegram_id=worker.telegram_id)

@views_bp.route("/operator/send_message/<int:request_id>", methods=["POST"])
@login_required
def send_operator_message(request_id):
    req = SupportRequest.query.get_or_404(request_id)
    if req.operator_id != current_user.id or req.status == "closed":
        abort(403)

    text = request.form.get("text", "").strip()
    files = request.files.getlist("media")

    media = []
    os.makedirs("static/media", exist_ok=True)
    for file in files[:5]:
        if file.filename:
            fname = f"media/{uuid.uuid4().hex}_{file.filename}"
            file.save(os.path.join("static", fname))
            media.append(f"/static/{fname}")

    if not text and not media:
        flash("Нельзя отправить пустое сообщение.")
        return redirect(url_for("views.chat", request_id=request_id))

    new_msg = SupportMessage(
        request_id=request_id,
        sender_role="admin",
        text=text if text else None,
        media=media if media else None,
        created_at=datetime.utcnow()
    )
    db.session.add(new_msg)
    db.session.commit()

    return redirect(url_for("views.chat", request_id=request_id))

@views_bp.route("/operator/close_request/<int:request_id>", methods=["POST"])
@login_required
def close_request(request_id):
    req = SupportRequest.query.get_or_404(request_id)
    if req.operator_id != current_user.id:
        abort(403)

    req.status = "closed"
    req.closed_at = datetime.utcnow()
    db.session.add(SupportMessage(
        request_id=request_id,
        sender_role="admin",
        text="Обращение закрыто оператором.",
        created_at=datetime.utcnow()
    ))
    db.session.commit()
    return redirect(url_for("views.list_requests", status="closed"))

@views_bp.route("/operator/exit_chat")
@login_required
def exit_chat():
    return redirect(url_for("views.index"))

@views_bp.route("/chat/<token>/<int:telegram_id>", methods=["GET", "POST"])
def user_chat(token, telegram_id):
    req = SupportRequest.query.filter_by(session_token=token).first()
    if not req:
        abort(404)

    worker = Worker.query.get(req.worker_id)
    if not worker or worker.telegram_id != telegram_id:
        abort(404)

    messages_db = SupportMessage.query.filter_by(request_id=req.id).order_by(SupportMessage.created_at).all()

    messages = []
    for msg in messages_db:
        messages.append({
            "sender": msg.sender_role,
            "text": msg.text,
            "created_at": msg.created_at,
            "media": msg.media or []
        })

    if request.method == "POST":
        if req.status == "closed":
            flash("Обращение закрыто. Отправлять сообщения нельзя.")
            return redirect(url_for("views.user_chat", token=token, telegram_id=telegram_id))

        text = request.form.get("text", "").strip()
        files = request.files.getlist("media")

        media = []
        os.makedirs("static/media", exist_ok=True)
        for file in files[:5]:
            if file.filename:
                fname = f"media/{uuid.uuid4().hex}_{file.filename}"
                file.save(os.path.join("static", fname))
                media.append(f"/static/{fname}")

        if not text and not media:
            flash("Нельзя отправить пустое сообщение.")
            return redirect(url_for("views.user_chat", token=token, telegram_id=telegram_id))

        new_msg = SupportMessage(
            request_id=req.id,
            sender_role="user",
            text=text if text else None,
            media=media if media else None,
            created_at=datetime.utcnow()
        )
        db.session.add(new_msg)
        db.session.commit()

        return redirect(url_for("views.user_chat", token=token, telegram_id=telegram_id))

    return render_template("user_chat.html",
                           messages=messages,
                           status=req.status,
                           full_name=worker.full_name,
                           token=token,
                           telegram_id=telegram_id)

