from django.shortcuts import render,redirect
from .forms import RegisterForm, LoginForm,PostForm
from .models import Users,Post,Like, Comment
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
#
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer
# Create your views here.

@csrf_exempt
def home(request):
    if 'username' not in request.session:
        return redirect('login')

    current_user = Users.objects.get(username=request.session['username'])

    # Handle Post Creation
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)

        if post_form.is_valid():
            content = post_form.cleaned_data.get("content")
            image = post_form.cleaned_data.get("image")

            if not content and not image:
                messages.error(request, "Please add content or image before posting.")
                return redirect('home')

            new_post = post_form.save(commit=False)
            new_post.user = current_user
            new_post.save()
            messages.success(request, "Post added successfully!")
            return redirect("home")

    else:
        post_form = PostForm()

    # Load all posts
    all_posts = Post.objects.all().order_by('-created_at')

    # Attach is_liked flag
    for p in all_posts:
        p.is_liked = Like.objects.filter(user=current_user, post=p).exists()
    view_user = request.GET.get("view_user")

    if view_user:
        # Show only selected user's posts
        all_posts = Post.objects.filter(user__username=view_user).order_by("-created_at")
    else:
        # Show all posts
        all_posts = Post.objects.all().order_by("-created_at")

    for p in all_posts:
        p.is_liked = Like.objects.filter(user=current_user, post=p).exists() 

    context = {
        "current_user": current_user,
        "all_posts": all_posts,
    }
    
    return render(request, "home.html", {
        "current_user": current_user,
        "post_form": post_form,
        "all_posts": all_posts,     # MUST match home.html
    })

def logout_view(request):
    if 'username' in request.session:
        del request.session['username']  # clear session
    return redirect('login')


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = Users.objects.get(username=username)
                if check_password(password, user.password):
                    request.session['username'] = user.username
                    return redirect('home')
                else:
                    messages.error(request, "Invalid username or password")
            except Users.DoesNotExist:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if password != confirm_password:
                messages.error(request, "Passwords do not match")
            elif Users.objects.filter(username=username).exists():
                messages.error(request, "Username already taken")
            else:
                # Hash password
                Users.objects.create(username=username, password=make_password(password))
                messages.success(request, "Registration successful!")
                return redirect('login')
    else:
        form = RegisterForm()
    return render(request, "register.html", {'form': form})

@csrf_exempt
def like_post(request, post_id):
    if 'username' not in request.session:
        return JsonResponse({'error': 'Not logged in'}, status=403)

    user = Users.objects.get(username=request.session['username'])
    post = Post.objects.get(id=post_id)

    existing_like = Like.objects.filter(user=user, post=post)

    if existing_like.exists():
        existing_like.delete()
        liked = False
    else:
        Like.objects.create(user=user, post=post)
        liked = True

    like_count = Like.objects.filter(post=post).count()

    # ✔ FIX: rename like_count → count (what JS expects)
    return JsonResponse({
        'liked': liked,
        'count': like_count
    })


def comment_list(request, post_id):
    comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')

    data = [
        {
            "user": c.user.username,
            "text": c.text,
            "created": c.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for c in comments
    ]
    return JsonResponse({"comments": data})

@csrf_exempt
def add_comment(request, post_id):
    if 'username' not in request.session:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.method == "POST":
        user = Users.objects.get(username=request.session['username'])
        text = request.POST.get("text")

        if not text:
            return JsonResponse({"error": "Comment cannot be empty"}, status=400)

        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(user=user, post=post, text=text)

        return JsonResponse({
            "success": True,
            "user": user.username,
            "text": comment.text,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def delete_post(request, post_id):
    if 'username' not in request.session:
        return JsonResponse({"error": "Not logged in"}, status=401)

    try:
        post = Post.objects.get(id=post_id)
        if post.user.username != request.session['username']:
            return JsonResponse({"error": "Not allowed"}, status=403)

        post.delete()
        return JsonResponse({"success": True})
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

@csrf_exempt
def edit_post(request, post_id):
    if 'username' not in request.session:
        return JsonResponse({"success": False, "error": "Login required"})

    post = Post.objects.get(id=post_id)

    if post.user.username != request.session['username']:
        return JsonResponse({"success": False, "error": "Not allowed"})

    if request.method == "POST":
        content = request.POST.get("text")
        image = request.FILES.get("image")

        post.content = content
        if image:
            post.image = image

        post.save()

        return JsonResponse({
            "success": True,
            "image_url": post.image.url if image else None
        })

    return JsonResponse({"success": False, "error": "Invalid request"})

@csrf_exempt
def update_profile_image(request):
    if 'username' not in request.session:
        return JsonResponse({
            "success": False,
            "error": "Login required"
        })

    user = Users.objects.get(username=request.session['username'])
    if request.method == "POST":
        image = request.FILES.get("profile_image")

        if not image:
            return JsonResponse({
                "success": False,
                "error": "No image selected"
            })

        user.profile_image = image
        user.save()

        return JsonResponse({
            "success": True,
            "image_url": user.profile_image.url
        })

    return JsonResponse({
        "success": False,
        "error": "Invalid request"
    })

#rest api framework method
@api_view(['POST'])
def create_post(request):
    serializer = PostSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Post created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_post_api(request):
    username = request.data.get("user")
    post_id = request.data.get("id")
    if not username:
        return Response(
            {"error": "Username is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = Users.objects.get(username=username)
    except Users.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {"error": "Post not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # OWNER CHECK
    if post.user != user:
        return Response(
            {"error": "You are not allowed to delete this post"},
            status=status.HTTP_403_FORBIDDEN
        )

    post.delete()
    return Response(
        {"message": "Post deleted successfully"},
        status=status.HTTP_200_OK
    )

@api_view(['PATCH'])
def edit_post_api(request):
    username = request.data.get("user")
    post_id = request.data.get("id")

    if not username or not post_id:
        return Response(
            {"error": "user and id are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 1 Get user
    try:
        user = Users.objects.get(username=username)
    except Users.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2 Get post
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {"error": "Post not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 3 OWNER CHECK 
    if post.user != user:
        return Response(
            {"error": "You are not allowed to edit this post"},
            status=status.HTTP_403_FORBIDDEN
        )

    # 4 UPDATE FIELDS (partial)
    content = request.data.get("content")
    image = request.FILES.get("image")

    if content is not None:
        post.content = content

    if image is not None:
        post.image = image

    post.save()

    return Response(
        {"message": "Post updated successfully"},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def posts_by_user(request):
    username = request.GET.get("username")  # note that GET paramater is used here

    if not username:
        return Response(
            {"error": "Username is required as query parameter"},
            status=status.HTTP_400_BAD_REQUEST
        )

    #Get user
    try:
        user = Users.objects.get(username=username)
    except Users.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get posts
    posts = Post.objects.filter(user=user).order_by('-created_at')

    # serialize
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


