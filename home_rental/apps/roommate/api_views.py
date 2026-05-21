"""
NestMate — Roommate API Views (JSON responses)
Used by AJAX calls, live score preview, and mobile app.
"""

"""
NestMate — Roommate API Views
"""

import json
from datetime import datetime

from django.http      import JsonResponse
from django.views     import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators        import method_decorator

from apps.accounts.models  import User
from apps.listings.models  import RoommateProfile, RoommateMatch
from ml.roommate_matching  import calculate_compatibility


def get_mongo_user(django_user):
    return User.objects(email=django_user.email).first()


def profile_to_dict(profile, user=None):
    return {
        'user_id':        str(profile.user.id) if profile.user else '',
        'name':           profile.user.full_name or profile.user.username if profile.user else '',
        'age':            profile.age,
        'gender':         profile.gender,
        'profession':     profile.profession or '',
        'city':           profile.city,
        'locality':       profile.locality or '',
        'budget_min':     profile.budget_min,
        'budget_max':     profile.budget_max,
        'sleep_schedule': profile.sleep_schedule,
        'smoking':        profile.smoking,
        'drinking':       profile.drinking,
        'pets':           profile.pets,
        'cleanliness':    profile.cleanliness,
        'guests_frequency': profile.guests_frequency,
        'work_schedule':  profile.work_schedule,
        'diet':           profile.diet,
        'gender_pref':    profile.gender_pref,
        'about':          profile.about or '',
        'is_looking':     profile.is_looking,
        'avatar_url':     profile.user.avatar_url or '' if profile.user else '',
    }


# ══════════════════════════════════════════════════════════════════════════════
# 1. SAVE / GET MY PROFILE  —  POST /api/roommate/profile/me/
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class MyProfileView(View):

    def get(self, request):
        mongo_user = get_mongo_user(request.user)
        profile    = RoommateProfile.objects(user=mongo_user).first()
        if not profile:
            return JsonResponse({'profile': None})
        return JsonResponse({'profile': profile_to_dict(profile)})

    def post(self, request):
        mongo_user = get_mongo_user(request.user)
        if not mongo_user:
            return JsonResponse({'error': 'User not found'}, status=404)

        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST.dict()

        # Get or create profile
        profile = RoommateProfile.objects(user=mongo_user).first()
        if not profile:
            profile = RoommateProfile(user=mongo_user)

        # Update all fields
        profile.age              = int(data.get('age') or 0) or None
        profile.gender           = data.get('gender',          'other')
        profile.profession       = data.get('profession',      '')
        profile.city             = data.get('city',            '')
        profile.locality         = data.get('locality',        '')
        profile.budget_min       = int(data.get('budget_min')  or 0)
        profile.budget_max       = int(data.get('budget_max')  or 0)
        profile.sleep_schedule   = data.get('sleep_schedule',  'flexible')
        profile.smoking          = bool(data.get('smoking') in [True, 'true', 'True', 1, '1'])
        profile.drinking         = bool(data.get('drinking') in [True, 'true', 'True', 1, '1'])
        profile.pets             = bool(data.get('pets') in [True, 'true', 'True', 1, '1'])
        profile.cleanliness      = int(data.get('cleanliness') or 3)
        profile.guests_frequency = data.get('guests_frequency', 'rarely')
        profile.work_schedule    = data.get('work_schedule',    'day_shift')
        profile.diet             = data.get('diet',             'any')
        profile.gender_pref      = data.get('gender_pref',     'any')
        profile.about            = data.get('about',           '')
        profile.is_looking       = True
        profile.updated_at       = datetime.utcnow()
        profile.save()

        return JsonResponse({
            'message': 'Profile saved',
            'profile': profile_to_dict(profile),
        })


# ══════════════════════════════════════════════════════════════════════════════
# 2. GET MATCHES  —  GET /api/roommate/matches/
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class MatchesAPIView(View):

    def get(self, request):
        mongo_user = get_mongo_user(request.user)
        if not mongo_user:
            return JsonResponse({'error': 'User not found'}, status=404)

        my_profile = RoommateProfile.objects(user=mongo_user).first()
        if not my_profile:
            return JsonResponse(
                {'error': 'Please complete your roommate profile first.'},
                status=400
            )

        # Get ALL other profiles that are looking
        # Include profiles even from same city for testing
        # Get ALL other profiles — don't filter by is_looking
        # because old profiles don't have this field
        other_profiles = RoommateProfile.objects(
            user__ne = mongo_user,
        )

        # If city filter, apply it — but ONLY if there are results
        city_profiles = RoommateProfile.objects(
            user__ne = mongo_user,
            city     = my_profile.city,
        ) if my_profile.city else other_profiles

        # Use city profiles if available, else fall back to all profiles
        candidates = list(city_profiles) if city_profiles.count() > 0 else list(other_profiles)

        # Calculate compatibility for each
        matches = []
        for other in candidates:
            try:
                result = calculate_compatibility(
                    profile_a=my_profile,
                    profile_b=other,
                )

                # Include ALL matches (even low scores) for testing
                # In production use: if result['score'] >= 30
                matches.append({
                    'score':      round(result['score'], 1),
                    'verdict':    result.get('verdict', ''),
                    'highlights': result.get('highlights', []),
                    'conflicts':  result.get('conflicts',  []),
                    'breakdown':  result.get('breakdown',  {}),
                    'candidate':  profile_to_dict(other),
                })
            except Exception as e:
                # Skip this profile if scoring fails
                continue

        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)

        return JsonResponse({
            'matches': matches,
            'total':   len(matches),
            'city':    my_profile.city or '',
        })


# ══════════════════════════════════════════════════════════════════════════════
# 3. ALL PROFILES  —  GET /api/roommate/profiles/
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class ProfilesAPIView(View):

    def get(self, request):
        city  = request.GET.get('city',  '')
        limit = int(request.GET.get('limit', 20))

        filters = {'is_looking': True}
        if city:
            filters['city'] = city

        profiles = list(
            RoommateProfile.objects(**filters).limit(limit)
        )

        return JsonResponse({
            'profiles': [profile_to_dict(p) for p in profiles],
            'total':    len(profiles),
        })


# ══════════════════════════════════════════════════════════════════════════════
# 4. SINGLE PROFILE  —  GET /api/roommate/profile/<user_id>/
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class ProfileDetailAPIView(View):

    def get(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except Exception:
            return JsonResponse({'error': 'User not found'}, status=404)

        profile = RoommateProfile.objects(user=target_user).first()
        if not profile:
            return JsonResponse({'error': 'Profile not found'}, status=404)

        return JsonResponse({'profile': profile_to_dict(profile)})


# ══════════════════════════════════════════════════════════════════════════════
# 5. SCORE TWO PROFILES  —  POST /api/roommate/score/
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class ScoreAPIView(View):

    def post(self, request):
        mongo_user = get_mongo_user(request.user)
        if not mongo_user:
            return JsonResponse({'error': 'User not found'}, status=404)

        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST.dict()

        # If saving profile data, route to MyProfileView
        if any(k in data for k in ['city', 'budget_min', 'sleep_schedule']):
            view = MyProfileView()
            view.request = request
            return view.post(request)

        # Otherwise calculate score between two user IDs
        user_a_id = data.get('user_a_id', '')
        user_b_id = data.get('user_b_id', '')

        if not user_a_id or not user_b_id:
            return JsonResponse({'error': 'user_a_id and user_b_id required'}, status=400)

        try:
            user_a    = User.objects.get(id=user_a_id)
            user_b    = User.objects.get(id=user_b_id)
            profile_a = RoommateProfile.objects(user=user_a).first()
            profile_b = RoommateProfile.objects(user=user_b).first()

            if not profile_a or not profile_b:
                return JsonResponse({'error': 'One or both profiles not found'}, status=404)

            result = calculate_compatibility(profile_a, profile_b)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# ══════════════════════════════════════════════════════════════════════════════
# 6. CITY STATS  —  GET /api/roommate/city-stats/
# ══════════════════════════════════════════════════════════════════════════════

class CityStatsAPIView(View):

    def get(self, request):
        cities = [
            'Mumbai', 'Pune', 'Bangalore', 'Delhi',
            'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad',
        ]
        stats = {}
        for city in cities:
            count = RoommateProfile.objects(
                city=city,
                is_looking=True,
            ).count()
            if count > 0:
                stats[city] = count

        return JsonResponse({'stats': stats})


# ══════════════════════════════════════════════════════════════════════════════
# 7. COMPARE TWO USERS  —  GET /api/roommate/compare/<user_id>/
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class CompareAPIView(View):

    def get(self, request, user_id):
        mongo_user = get_mongo_user(request.user)
        my_profile = RoommateProfile.objects(user=mongo_user).first()

        if not my_profile:
            return JsonResponse({'error': 'Complete your profile first'}, status=400)

        try:
            other_user    = User.objects.get(id=user_id)
            other_profile = RoommateProfile.objects(user=other_user).first()
        except Exception:
            return JsonResponse({'error': 'User not found'}, status=404)

        if not other_profile:
            return JsonResponse({'error': 'Other user has no profile'}, status=404)

        result = calculate_compatibility(my_profile, other_profile)
        return JsonResponse({
            **result,
            'my_profile':    profile_to_dict(my_profile),
            'other_profile': profile_to_dict(other_profile),
        })