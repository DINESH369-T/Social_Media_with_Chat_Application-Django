
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from chat.models import Message
from proj_3.models import Users


def chat_room(request, username):

    # Check login
    if "username" not in request.session:
        return redirect("login")

    current_user = get_object_or_404(
        Users,
        username=request.session["username"]
    )

    other_user = get_object_or_404(
        Users,
        username=username
    )

    # Prevent opening a chat with yourself
    if current_user == other_user:
        return redirect("inbox")

    # Generate consistent room name
    room_name = "_".join(
        sorted([current_user.username, other_user.username])
    )

    # Retrieve conversation messages
    messages = Message.objects.filter(
        (Q(sender=current_user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=current_user))
    ).select_related(
        "sender", "receiver"
    ).order_by("timestamp")

    return render(request, "chat_room.html", {
        "current_user": current_user,
        "other_user": other_user,
        "messages": messages,
        "room_name": room_name,
    })


def inbox(request):

    # Check login
    if "username" not in request.session:
        return redirect("login")

    current_user = get_object_or_404(
        Users,
        username=request.session["username"]
    )

    # Retrieve all messages involving the current user
    chats = Message.objects.filter(
        Q(sender=current_user) |
        Q(receiver=current_user)
    ).select_related(
        "sender", "receiver"
    ).order_by("-timestamp")

    # Collect unique conversation users
    users = {}

    for msg in chats:

        if msg.sender != current_user:
            users[msg.sender.id] = msg.sender

        if msg.receiver != current_user:
            users[msg.receiver.id] = msg.receiver

    # Sort conversations alphabetically
    users = sorted(
        users.values(),
        key=lambda user: user.username.lower()
    )

    return render(request, "inbox.html", {
        "users": users
    })
