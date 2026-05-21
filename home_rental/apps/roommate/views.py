"""
NestMate — Roommate Matching Views
Feature 1: AI-Based Roommate Matching
Handles: Landing, Questionnaire, Matches, Profile View,
         Connect Request, Saved Matches
"""

import json
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View

from apps.listings.models import RoommateProfile, RoommateMatch
from apps.accounts.models import User
from ml.roommate_matching import calculate_compatibility 


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_mongo_user(django_user):
    """Resolve Django session user → MongoEngine User by email."""
    return User.objects(email=django_user.email).first()


def profile_to_dict(profile: RoommateProfile) -> dict:
    """
    Convert a RoommateProfile MongoEngine document
    into a plain dict for the ML matching module.
    """
    return {
        'user_id':          str(profile.user.id),
        'name':             profile.user.full_name or profile.user.username,
        'avatar':           profile.user.avatar_url or '',
        'profession':       profile.profession or '',
        'about':            profile.about or '',
        'age':              profile.age or 0,
        'gender':           profile.gender or 'other',
        'city':             profile.city,
        'locality':         profile.locality or '',
        'budget_min':       profile.budget_min,
        'budget_max':       profile.budget_max,
        'sleep_schedule':   profile.sleep_schedule,
        'smoking':          profile.smoking,
        'drinking':         profile.drinking,
        'pets':             profile.pets,
        'cleanliness':      profile.cleanliness,
        'guests_frequency': profile.guests_frequency,
        'work_schedule':    profile.work_schedule,
        'diet':             profile.diet,
        'gender_pref':      profile.gender_pref,
        'is_looking':       profile.is_looking,
        'created_at':       profile.created_at.strftime('%d %b %Y')
                            if profile.created_at else '',
    }


def _gender_is_compatible(my_profile: dict, their_profile: dict) -> bool:
    """
    Check if gender preferences are mutually compatible.
    Returns False only if there is a hard conflict.
    """
    my_pref    = my_profile.get('gender_pref', 'any')
    their_pref = their_profile.get('gender_pref', 'any')
    my_gender  = my_profile.get('gender', 'other')
    their_gender = their_profile.get('gender', 'other')

    # Check if they accept my gender
    if their_pref != 'any' and their_pref != my_gender:
        return False
    # Check if I accept their gender
    if my_pref != 'any' and my_pref != their_gender:
        return False

    return True


def _dict_to_obj(data: dict):
    class _ProfileObject:
        pass

    obj = _ProfileObject()
    for key, value in (data or {}).items():
        setattr(obj, key, value)
    return obj


    """
    Score candidate roommate profiles against the user's profile.
    Returns top matches sorted by compatibility score.
    """
    my_obj = _dict_to_obj(my_profile)
    matches = []

    for candidate in candidate_profiles:
        candidate_obj = _dict_to_obj(candidate)
        compat = calculate_compatibility(my_obj, candidate_obj)
        matches.append({
            'candidate': candidate,
            'score': compat.get('score', 0),
            'compatibility': compat,
        })

    return sorted(matches, key=lambda item: item['score'], reverse=True)[:top_n]


# ══════════════════════════════════════════════════════════════════════════════
# 1. LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════

class RoommateHomeView(View):
    """
    Landing page for the roommate matching feature.
    Shows how it works, success stories, and CTA to take quiz.
    """
    def get(self, request):
        # Count active seekers in each city for social proof
        city_counts = {}
        for city in ['Mumbai', 'Pune', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai']:
            city_counts[city] = RoommateProfile.objects(
                city=city, is_looking=True
            ).count()

        # Recent matches count
        total_matches = RoommateMatch.objects.count()

        payload = {
            'city_counts':   city_counts,
            'total_matches': total_matches,
            'steps': [
                {
                    'icon':  '📋',
                    'title': 'Fill the Quiz',
                    'desc':  'Answer 10 questions about your budget, lifestyle, and habits.'
                },
                {
                    'icon':  '🤖',
                    'title': 'AI Matches You',
                    'desc':  'Our algorithm scores compatibility across 8 dimensions.'
                },
                {
                    'icon':  '🤝',
                    'title': 'Connect & Move In',
                    'desc':  'Chat with your top matches and find your perfect roommate.'
                },
            ],
        }
        return JsonResponse(payload)


# ══════════════════════════════════════════════════════════════════════════════
# 2. QUESTIONNAIRE (Multi-step form)
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class RoommateQuestionnaireView(View):
    """
    4-step personality and lifestyle questionnaire.
    Creates or updates the user's RoommateProfile.
    GET  → show form (prefilled if profile exists)
    POST → save profile → redirect to matches
    """

    def get(self, request):
        mongo_user = get_mongo_user(request.user)
        profile    = None

        if mongo_user:
            profile = RoommateProfile.objects(user=mongo_user).first()

        payload = {
            'profile': profile_to_dict(profile) if profile else None,
            'cities': [
                'Mumbai', 'Pune', 'Bangalore', 'Delhi',
                'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad'
            ],
            # Pre-built options for radio/select fields
            'sleep_options': [
                {'value': 'early_bird', 'label': '🌅 Early Bird',  'desc': 'Asleep by 10 PM'},
                {'value': 'flexible',   'label': '😎 Flexible',    'desc': 'Adapt to roommate'},
                {'value': 'night_owl',  'label': '🦉 Night Owl',   'desc': 'Up past midnight'},
            ],
            'work_options': [
                {'value': 'day_shift',   'label': '💼 Day Shift',     'desc': '9 AM – 6 PM'},
                {'value': 'night_shift', 'label': '🌙 Night Shift',   'desc': 'Evening / Night'},
                {'value': 'wfh',         'label': '🏠 Work From Home','desc': 'Home all day'},
                {'value': 'student',     'label': '🎓 Student',       'desc': 'College schedule'},
            ],
            'diet_options': [
                {'value': 'any',     'label': '🍽️ No Preference'},
                {'value': 'veg',     'label': '🥗 Vegetarian'},
                {'value': 'non_veg', 'label': '🍗 Non-Vegetarian'},
                {'value': 'vegan',   'label': '🌱 Vegan'},
            ],
            'guest_options': [
                {'value': 'never',     'label': '🚫 Never'},
                {'value': 'rarely',    'label': '🤏 Rarely'},
                {'value': 'sometimes', 'label': '😊 Sometimes'},
                {'value': 'often',     'label': '🎉 Often'},
            ],
        }
        return JsonResponse(payload)

    def post(self, request):
        mongo_user = get_mongo_user(request.user)

        if not mongo_user:
            messages.error(request, 'Account not found. Please log in again.')
            return redirect('login')

        data = request.POST

        # ── Validate budget ────────────────────────────────────────────────────
        budget_min = data.get('budget_min', '').strip()
        budget_max = data.get('budget_max', '').strip()

        if not budget_min.isdigit() or not budget_max.isdigit():
            messages.error(request, '❌ Please enter valid budget amounts.')
            return redirect('roommate_questionnaire')

        budget_min = int(budget_min)
        budget_max = int(budget_max)

        if budget_min > budget_max:
            messages.error(request, '❌ Minimum budget cannot exceed maximum budget.')
            return redirect('roommate_questionnaire')

        # ── Validate city ──────────────────────────────────────────────────────
        city = data.get('city', '').strip()
        if not city:
            messages.error(request, '❌ Please select a city.')
            return redirect('roommate_questionnaire')

        # ── Upsert RoommateProfile ─────────────────────────────────────────────
        profile = RoommateProfile.objects(user=mongo_user).first()
        if not profile:
            profile = RoommateProfile(user=mongo_user)

        profile.budget_min       = budget_min
        profile.budget_max       = budget_max
        profile.city             = city
        profile.locality         = data.get('locality', '').strip()
        profile.sleep_schedule   = data.get('sleep_schedule', 'flexible')
        profile.smoking          = data.get('smoking', 'no') == 'yes'
        profile.drinking         = data.get('drinking', 'no') == 'yes'
        profile.pets             = data.get('pets', 'no') == 'yes'
        profile.cleanliness      = int(data.get('cleanliness', 3))
        profile.guests_frequency = data.get('guests_frequency', 'rarely')
        profile.work_schedule    = data.get('work_schedule', 'day_shift')
        profile.diet             = data.get('diet', 'any')
        profile.gender_pref      = data.get('gender_pref', 'any')
        profile.about            = data.get('about', '').strip()[:500]
        profile.profession       = data.get('profession', '').strip()
        profile.gender           = data.get('gender', 'other')
        profile.is_looking       = True
        profile.updated_at       = datetime.utcnow()

        age_raw = data.get('age', '').strip()
        if age_raw.isdigit():
            profile.age = int(age_raw)

        profile.save()

        # ── Update user full_name if provided ──────────────────────────────────
        full_name = data.get('full_name', '').strip()
        if full_name and not mongo_user.full_name:
            mongo_user.update(full_name=full_name)

        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'message': 'Profile saved',
                'profile': profile_to_dict(profile),
            })

        messages.success(request, '✅ Profile saved! Here are your best matches.')
        return redirect('roommate_matches')


# ══════════════════════════════════════════════════════════════════════════════
# 3. MATCHES LIST
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class RoommateMatchesView(View):
    """
    Shows top AI-matched roommates for the logged-in user.
    Filters by city, gender preference, and is_looking status.
    Sorted by compatibility score descending.
    """

    def get(self, request):
        mongo_user = get_mongo_user(request.user)

        # ── Must have a profile ────────────────────────────────────────────────
        my_profile = RoommateProfile.objects(user=mongo_user).first()
        if not my_profile:
            messages.info(
                request,
                '👋 Please complete your roommate profile first.'
            )
            return redirect('roommate_questionnaire')

        my_dict = profile_to_dict(my_profile)

        # ── Get candidate profiles in same city ────────────────────────────────
        # Exclude current user's profile using MongoEngine lookup
        candidates_qs = RoommateProfile.objects(
            city=my_profile.city,
            is_looking=True,
            user__ne=mongo_user,
        )

        # Apply gender preference filter at DB level
        if my_profile.gender_pref != 'any':
            candidates_qs = candidates_qs.filter(
                gender=my_profile.gender_pref
            )

        candidates = list(candidates_qs)

        # ── Convert to dicts ───────────────────────────────────────────────────
        candidate_dicts = [profile_to_dict(p) for p in candidates]

        # ── Run AI matching ────────────────────────────────────────────────────
        raw_matches = find_top_matches(my_dict, candidate_dicts, top_n=20)

        # ── Apply mutual gender compatibility filter ────────────────────────────
        matches = []
        for m in raw_matches:
            if _gender_is_compatible(my_dict, m['candidate']):
                matches.append(m)

        # ── Check which users I've already connected with ──────────────────────
        sent_requests = set(
            str(r.user_b.id)
            for r in RoommateMatch.objects(user_a=mongo_user)
        )

        # ── Attach connection status to each match ─────────────────────────────
        for m in matches:
            m['already_connected'] = m['candidate']['user_id'] in sent_requests

        # ── Stats for the page header ──────────────────────────────────────────
        avg_score = (
            round(sum(m['score'] for m in matches) / len(matches), 1)
            if matches else 0
        )

        return JsonResponse({
            'error': 'Roommate matches pages are deprecated. Use React frontend routes.',
            'deprecated': True,
        }, status=410)


# ══════════════════════════════════════════════════════════════════════════════
# 4. PUBLIC ROOMMATE PROFILE
# ══════════════════════════════════════════════════════════════════════════════

class RoommateProfileView(View):
    """
    View another user's roommate profile.
    Shows their bio, preferences, and your compatibility score.
    """

    def get(self, request, user_id):
        # Get the target user
        target_user = User.objects(id=user_id, is_active=True).first()
        if not target_user:
            messages.error(request, 'User not found.')
            return redirect('roommate_home')

        target_profile = RoommateProfile.objects(
            user=target_user, is_looking=True
        ).first()
        if not target_profile:
            messages.error(request, 'This user has no active roommate profile.')
            return redirect('roommate_home')

        # ── Compute compatibility if logged in ─────────────────────────────────
        compat_result = None
        if request.user.is_authenticated:
            mongo_user = get_mongo_user(request.user)
            my_profile = RoommateProfile.objects(user=mongo_user).first()
            if my_profile and str(mongo_user.id) != user_id:
                compat_result = calculate_compatibility(
                    profile_to_dict(my_profile),
                    profile_to_dict(target_profile),
                )

        # ── Check if already connected ─────────────────────────────────────────
        already_connected = False
        if request.user.is_authenticated:
            mongo_user = get_mongo_user(request.user)
            already_connected = bool(
                RoommateMatch.objects(
                    user_a=mongo_user,
                    user_b=target_user,
                ).first()
            )

        # If the client expects JSON (React frontend), return profile payload
        accept = request.headers.get('Accept', '')
        if 'application/json' in accept:
            return JsonResponse({
                'profile': profile_to_dict(target_profile),
                'compatibility': compat_result,
                'already_connected': already_connected,
            })

        # Otherwise keep the deprecation response for browser navigations
        return JsonResponse({
            'error': 'Roommate profile pages are deprecated. Use React frontend routes.',
            'deprecated': True,
        }, status=410)


# ══════════════════════════════════════════════════════════════════════════════
# 5. SEND CONNECT REQUEST
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class SendConnectRequestView(View):
    def post(self, request, user_id):
        import json
        mongo_user = get_mongo_user(request.user)
        if not mongo_user:
            return JsonResponse({'error': 'User not found'}, status=404)

        try:
            target_user = User.objects.get(id=user_id)
        except Exception:
            return JsonResponse({'error': 'Target user not found'}, status=404)

        if str(mongo_user.id) == str(target_user.id):
            return JsonResponse({'error': 'Cannot connect with yourself'}, status=400)

        # Check if already sent
        existing = RoommateMatch.objects(
            user_a=mongo_user,
            user_b=target_user,
        ).first() or RoommateMatch.objects(
            user_a=target_user,
            user_b=mongo_user,
        ).first()

        if existing:
            return JsonResponse({
                'message':  'Request already sent',
                'match_id': str(existing.id),
                'status':   existing.status,
            })

        # Create match request
        match = RoommateMatch(
            user_a     = mongo_user,
            user_b     = target_user,
            status     = 'pending',
            created_at = datetime.utcnow(),
        )
        match.save()

        return JsonResponse({
            'message':  'Connection request sent!',
            'match_id': str(match.id),
            'status':   'pending',
        }, status=201)

    def get(self, request, user_id):
        return JsonResponse({'error': 'Use POST'}, status=405)


# ══════════════════════════════════════════════════════════════════════════════
# 6. ACCEPT / REJECT REQUEST
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class RespondToRequestView(View):
    def post(self, request, match_id):
        import json
        mongo_user = get_mongo_user(request.user)

        try:
            data   = json.loads(request.body)
            action = data.get('action', '')
        except Exception:
            action = request.POST.get('action', '')

        try:
            match = RoommateMatch.objects.get(id=match_id)
        except Exception:
            return JsonResponse({'error': 'Request not found'}, status=404)

        # Only the recipient (user_b) can respond
        if str(match.user_b.id) != str(mongo_user.id):
            return JsonResponse({'error': 'Not authorized'}, status=403)

        if action == 'accept':
            match.update(status='accepted', responded_at=datetime.utcnow())
            return JsonResponse({'message': 'Request accepted!', 'status': 'accepted'})
        elif action == 'decline':
            match.update(status='declined', responded_at=datetime.utcnow())
            return JsonResponse({'message': 'Request declined', 'status': 'declined'})
        else:
            return JsonResponse({'error': 'Invalid action. Use accept or decline'}, status=400)


# ══════════════════════════════════════════════════════════════════════════════
# 7. MY REQUESTS (Inbox)
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class RoommateRequestsView(View):
    def get(self, request):
        mongo_user = get_mongo_user(request.user)
        if not mongo_user:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Fetch all — filter in Python to avoid missing field errors
        all_received = list(
            RoommateMatch.objects(user_b=mongo_user).order_by('-created_at')
        )
        all_sent = list(
            RoommateMatch.objects(user_a=mongo_user).order_by('-created_at')
        )

        # Filter pending in Python
        received = [m for m in all_received if getattr(m, 'status', 'pending') == 'pending']
        sent     = all_sent

        def match_to_dict(m, perspective):
            other = m.user_a if perspective == 'received' else m.user_b
            return {
                'match_id':   str(m.id),
                'status':     m.status,
                'created_at': m.created_at.isoformat() if m.created_at else '',
                'other_user': {
                    'id':         str(other.id) if other else '',
                    'name':       other.full_name or other.username if other else '',
                    'avatar_url': other.avatar_url or '' if other else '',
                    'city':       other.city or '' if other else '',
                },
            }

        return JsonResponse({
            'received': [match_to_dict(m, 'received') for m in received],
            'sent':     [match_to_dict(m, 'sent')     for m in sent],
            'pending_count': len(received),
        })


# ══════════════════════════════════════════════════════════════════════════════
# 8. UPDATE LOOKING STATUS
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class ToggleLookingView(View):
    """
    POST: Toggle whether the user is actively looking for a roommate.
    Hides profile from search results when is_looking=False.
    """

    def post(self, request):
        mongo_user = get_mongo_user(request.user)
        profile    = RoommateProfile.objects(user=mongo_user).first()

        if not profile:
            messages.error(request, 'Profile not found.')
            return redirect('roommate_questionnaire')

        new_status = not profile.is_looking
        profile.update(is_looking=new_status, updated_at=datetime.utcnow())

        if new_status:
            messages.success(
                request,
                '✅ Your profile is now visible to potential roommates.'
            )
        else:
            messages.info(
                request,
                '👻 Your profile is now hidden. Toggle back when ready.'
            )

        return redirect('roommate_matches')


# ══════════════════════════════════════════════════════════════════════════════
# 9. DELETE PROFILE
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class DeleteRoommateProfileView(View):
    """
    POST: Permanently delete the user's roommate profile and all their matches.
    """

    def post(self, request):
        mongo_user = get_mongo_user(request.user)
        profile    = RoommateProfile.objects(user=mongo_user).first()

        if profile:
            # Delete all associated matches
            RoommateMatch.objects(user_a=mongo_user).delete()
            RoommateMatch.objects(user_b=mongo_user).delete()
            # Delete profile
            profile.delete()
            messages.success(
                request,
                '✅ Your roommate profile has been deleted.'
            )
        else:
            messages.error(request, 'No profile found.')

        return redirect('roommate_home')