"""
NestMate — Accounts Views
Handles: Register, Login, Logout, Profile, Verification Upload
"""

import os

import bcrypt
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from apps.accounts.models import User, VerificationDocument
from apps.accounts.forms import (
    RegisterForm, LoginForm,
    ProfileEditForm, VerificationForm, ChangePasswordForm
)


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: Get MongoDB user from Django session user
# ══════════════════════════════════════════════════════════════════════════════

def get_mongo_user(django_user):
    """
    Given a logged-in Django user, return the matching MongoEngine User.
    We match by email since both share the same email.
    """
    return User.objects(email=django_user.email).first()


# ══════════════════════════════════════════════════════════════════════════════
# REGISTER
# ══════════════════════════════════════════════════════════════════════════════

class RegisterView(View):
    def get(self, request):
        # Return CSRF cookie so React can read it
        return JsonResponse({'message': 'Ready to register'})

    def post(self, request):
        # Accept both JSON body (React) and form data
        import json
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
            else:
                body = request.POST.dict()
        except Exception:
            body = request.POST.dict()

        form = RegisterForm(body)
        if not form.is_valid():
            return JsonResponse(
                {'error': form.errors},
                status=400
            )

        d = form.cleaned_data
        hashed = bcrypt.hashpw(
            d['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')


        mongo_user = User(
            username  = d['username'],
            email     = d['email'],
            password  = hashed,
            full_name = d['full_name'],
            phone     = d.get('phone', ''),
            role      = d['role'],
            city      = d.get('city', ''),
        )
        mongo_user.compute_trust_score()
        mongo_user.save()


        django_user = DjangoUser.objects.create_user(
            username = d['username'],
            email    = d['email'],
            password = d['password'],
        )
        auth_login(
            request,
            django_user,
            backend='django.contrib.auth.backends.ModelBackend'
        )

        return JsonResponse({
            'message': 'Registered successfully',
            'user': {
                'id':        str(mongo_user.id),
                'username':  mongo_user.username,
                'email':     mongo_user.email,
                'full_name': mongo_user.full_name,
                'role':      mongo_user.role,
                'city':      mongo_user.city,
            }
        }, status=201)


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════════════

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            mongo_user = get_mongo_user(request.user)
            if mongo_user:
                return JsonResponse({
                    'user': {
                        'id':         str(mongo_user.id),
                        'username':   mongo_user.username,
                        'email':      mongo_user.email,
                        'full_name':  mongo_user.full_name,
                        'role':       mongo_user.role,
                        'city':       mongo_user.city,
                        'trust_score': mongo_user.trust_score,
                        'id_verified': mongo_user.id_verified,
                    }
                })
        return JsonResponse({'user': None})

    def post(self, request):
        import json
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
            else:
                body = request.POST.dict()
        except Exception:
            body = request.POST.dict()

        form = LoginForm(body)

        email    = body.get('email', '').lower().strip()
        password = body.get('password', '')

        mongo_user = User.objects(
            email=email, is_active=True
        ).first()

        if not mongo_user:
            return JsonResponse(
                {'error': 'No account found with this email.'},
                status=400
            )

        ok = bcrypt.checkpw(
            password.encode('utf-8'),
            mongo_user.password.encode('utf-8')
        )
        if not ok:
            return JsonResponse(
                {'error': 'Incorrect password.'},
                status=400
            )

        django_user, _ = DjangoUser.objects.get_or_create(
            email=email,
            defaults={'username': mongo_user.username}
        )
        auth_login(
            request,
            django_user,
            backend='django.contrib.auth.backends.ModelBackend'
        )
        mongo_user.update(last_login=datetime.utcnow())

        return JsonResponse({
            'message': 'Login successful',
            'user': {
                'id':          str(mongo_user.id),
                'username':    mongo_user.username,
                'email':       mongo_user.email,
                'full_name':   mongo_user.full_name,
                'role':        mongo_user.role,
                'city':        mongo_user.city,
                'trust_score': mongo_user.trust_score,
                'id_verified': mongo_user.id_verified,
                'avatar_url':  mongo_user.avatar_url,
            }
        })


# ══════════════════════════════════════════════════════════════════════════════
# LOGOUT
# ══════════════════════════════════════════════════════════════════════════════

class LogoutView(View):
    
    def post(self, request):
        auth_logout(request)
        return JsonResponse({'message': 'Logged out successfully'})

    def get(self, request):
        auth_logout(request)
        return JsonResponse({'message': 'Logged out successfully'})


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE PAGE
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        mongo_user = get_mongo_user(request.user)
        if not mongo_user:
            return JsonResponse({'error': 'Profile not found'}, status=404)

        from apps.listings.models import Listing
        my_listings = list(
            Listing.objects(owner=mongo_user).order_by('-created_at')
        )

        return JsonResponse({
            'id':                str(mongo_user.id),
            'username':          mongo_user.username,
            'email':             mongo_user.email,
            'full_name':         mongo_user.full_name or '',
            'phone':             mongo_user.phone or '',
            'bio':               mongo_user.bio or '',
            'city':              mongo_user.city or '',
            'locality':          mongo_user.locality or '',
            'role':              mongo_user.role,
            'avatar_url': (
                mongo_user.avatar_url
                if mongo_user.avatar_url and mongo_user.avatar_url.startswith('http')
                else f"http://localhost:8000{mongo_user.avatar_url}"
                if mongo_user.avatar_url
                else ''
            ),
            'id_verified':       mongo_user.id_verified,
            'bill_verified':     mongo_user.bill_verified,
            'email_verified':    mongo_user.email_verified,
            'trust_score':       mongo_user.trust_score,
            'verification_docs': [
                {
                    'doc_type':  d.doc_type,
                    'verified':  d.verified,
                    'file_url':  d.file_url,
                }
                for d in mongo_user.verification_docs
            ],
            'my_listings': [
                {
                    'id':    str(l.id),
                    'title': l.title,
                    'rent':  l.rent,
                    'photos': l.photos or [],
                    'trust_info': {
                        'score': l.trust_info.score if l.trust_info else 0
                    } if l.trust_info else None,
                    'is_available': l.is_available,
                }
                for l in my_listings
            ],
        })

    def post(self, request):
        mongo_user = get_mongo_user(request.user)
        form       = ProfileEditForm(request.POST, request.FILES)

        if not form.is_valid():
            return JsonResponse({'error': form.errors}, status=400)

        data       = form.cleaned_data
        avatar_url = mongo_user.avatar_url

        if request.FILES.get('avatar'):
            avatar     = request.FILES['avatar']

            # Validate file type
            allowed = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
            if hasattr(avatar, 'content_type') and avatar.content_type not in allowed:
                return JsonResponse(
                    {'error': 'Only JPG, PNG, WEBP images allowed.'},
                    status=400
                )

            upload_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
            os.makedirs(upload_dir, exist_ok=True)

            # Use a clean filename — avoid spaces and special chars
            import re
            clean_name = re.sub(r'[^a-zA-Z0-9._-]', '_', avatar.name)
            filename   = f'avatar_{str(mongo_user.id)}_{clean_name}'
            filepath   = os.path.join(upload_dir, filename)

            with open(filepath, 'wb+') as dest:
                for chunk in avatar.chunks():
                    dest.write(chunk)

            # Full URL so React can display it
            avatar_url = f'http://localhost:8000/media/avatars/{filename}'

        mongo_user.update(
            full_name  = data['full_name'],
            phone      = data.get('phone', ''),
            bio        = data.get('bio', ''),
            city       = data.get('city', ''),
            locality   = data.get('locality', ''),
            role       = data['role'],
            avatar_url = avatar_url,
            updated_at = datetime.utcnow(),
        )

        refreshed = User.objects.get(id=mongo_user.id)
        refreshed.compute_trust_score()
        refreshed.save()

        return JsonResponse({'message': 'Profile updated successfully'})


# ══════════════════════════════════════════════════════════════════════════════
# VERIFICATION UPLOAD (Feature 2 — Trust Score)
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class UploadVerificationView(View):
    def post(self, request):
        mongo_user = get_mongo_user(request.user)
        form       = VerificationForm(request.POST, request.FILES)

        if not form.is_valid():
            messages.error(request, 'Invalid file. Please try again.')
            return redirect('profile')

        data = form.cleaned_data
        file = request.FILES['document_file']

        # ── Save file to /media/verification/ ────────────────────────────────
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'verification')
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{mongo_user.id}_{data['doc_type']}_{file.name}"
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        file_url = f'/media/verification/{filename}'

        # ── Attach to user's verification_docs list ───────────────────────────
        doc = VerificationDocument(
            doc_type    = data['doc_type'],
            file_url    = file_url,
            verified    = False,           # Admin will approve later
            uploaded_at = datetime.utcnow(),
        )
        mongo_user.verification_docs.append(doc)
        mongo_user.save()

        # ── Auto-verify bill types immediately (demo behaviour) ───────────────
        # In production, admin reviews and approves
        if data['doc_type'] in ['electricity_bill', 'water_bill']:
            mongo_user.update(bill_verified=True)
            messages.success(request, '✅ Utility bill uploaded! Trust score updated.')
        elif data['doc_type'] in ['aadhaar', 'pan', 'passport', 'driving_license']:
            messages.success(request, '✅ ID uploaded! It will be verified within 24 hours.')
        
        # Recompute trust score
        refreshed = User.objects.get(id=mongo_user.id)
        refreshed.compute_trust_score()
        refreshed.save()

        return redirect('profile')


# ══════════════════════════════════════════════════════════════════════════════
# CHANGE PASSWORD
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    def post(self, request):
        mongo_user = get_mongo_user(request.user)
        form       = ChangePasswordForm(request.POST)

        if not form.is_valid():
            messages.error(request, 'Please fix the password errors.')
            return redirect('profile')

        data = form.cleaned_data

        # ── Verify current password ───────────────────────────────────────────
        current_ok = bcrypt.checkpw(
            data['current_password'].encode('utf-8'),
            mongo_user.password.encode('utf-8')
        )
        if not current_ok:
            messages.error(request, '❌ Current password is incorrect.')
            return redirect('profile')

        # ── Hash and save new password ────────────────────────────────────────
        new_hashed = bcrypt.hashpw(
            data['new_password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        mongo_user.update(password=new_hashed, updated_at=datetime.utcnow())

        # Update Django user password too
        request.user.set_password(data['new_password'])
        request.user.save()

        # Re-authenticate (Django logs out on password change)
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)

        messages.success(request, '✅ Password changed successfully!')
        return redirect('profile')


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC PROFILE (view another user's profile)
# ══════════════════════════════════════════════════════════════════════════════

class PublicProfileView(View):
    def get(self, request, user_id):
        user = User.objects(id=user_id, is_active=True).first()
        if not user:
            messages.error(request, 'User not found.')
            return redirect('home')

        from apps.listings.models import Listing, Review
        listings = Listing.objects(owner=user, is_available=True).limit(6)
        reviews  = Review.objects(listing__in=listings).order_by('-created_at').limit(5)

        return render(request, 'accounts/public_profile.html', {
            'profile_user': user,
            'listings':     list(listings),
            'reviews':      list(reviews),
        })


# ══════════════════════════════════════════════════════════════════════════════
# HELPER
# ══════════════════════════════════════════════════════════════════════════════

def _get_trust_breakdown(user: User) -> list:
    """
    Returns a list of trust score components for the profile page UI.
    Each item: { label, points, earned, icon }
    """
    return [
        {
            'label':  'Identity Verified',
            'icon':   '🪪',
            'points': 40,
            'earned': user.id_verified,
            'action': 'Upload Aadhaar / Passport',
        },
        {
            'label':  'Utility Bill Uploaded',
            'icon':   '💡',
            'points': 25,
            'earned': user.bill_verified,
            'action': 'Upload electricity or water bill',
        },
        {
            'label':  'Email Verified',
            'icon':   '📧',
            'points': 10,
            'earned': user.email_verified,
            'action': 'Verify your email address',
        },
        {
            'label':  'Phone Number Added',
            'icon':   '📱',
            'points': 10,
            'earned': bool(user.phone),
            'action': 'Add your phone number',
        },
        {
            'label':  'Profile Photo',
            'icon':   '🖼️',
            'points': 5,
            'earned': bool(user.avatar_url),
            'action': 'Upload a profile photo',
        },
        {
            'label':  'Bio Written',
            'icon':   '✍️',
            'points': 5,
            'earned': bool(user.bio),
            'action': 'Write something about yourself',
        },
        {
            'label':  'Full Name Added',
            'icon':   '👤',
            'points': 5,
            'earned': bool(user.full_name),
            'action': 'Add your full name',
        },
    ]