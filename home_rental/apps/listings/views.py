"""
NestMate — Listings Views
Features: Home, Search, Map Search, Detail, Create, Edit, Delete
          + Trust Score, Price Estimator, Scam Detection
"""
import math
from multiprocessing import context
import os
import json
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from django.conf import settings


from apps.listings.models import (
    Listing, Review, SavedListing,
    GeoLocation, TrustInfo, EnvironmentScore,
    NearbyAmenity
)
from apps.accounts.models import User
from ml.price_estimator import estimate_price, detect_scam


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_mongo_user(django_user):
    """Resolve Django auth user → MongoEngine User by email."""
    return User.objects(email=django_user.email).first()


def _compute_trust_score(trust: TrustInfo) -> int:
    score = 0
    if trust.id_verified:       score += 40
    if trust.bill_uploaded:     score += 25
    if trust.video_walkthrough: score += 20
    score += min(15, trust.reviews_count * 3)
    return min(100, score)


def _save_photos(files, listing_id: str) -> list:
    """Save uploaded photos to /media/listings/ and return URL list."""
    urls      = []
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'listings', str(listing_id))
    os.makedirs(upload_dir, exist_ok=True)
    for f in files:
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{f.name}"
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        urls.append(f'/media/listings/{listing_id}/{filename}')
    return urls


def _listing_to_dict(listing) -> dict:
    """Convert a Listing object to a dictionary for JSON responses."""
    return {
        'id': str(listing.id),
        'title': listing.title,
        'rent': listing.rent,
        'deposit': listing.deposit,
        'listing_type': listing.listing_type,
        'bedrooms': listing.bedrooms,
        'bathrooms': listing.bathrooms,
        'area_sqft': listing.area_sqft,
        'furnished': listing.furnished,
        'city': listing.location.city if listing.location else '',
        'locality': listing.location.locality if listing.location else '',
        'photos': listing.photos[:1] if listing.photos else [],
        'trust_score': listing.trust_info.score if listing.trust_info else 0,
        'is_available': listing.is_available,
    }


# ══════════════════════════════════════════════════════════════════════════════
# HOME VIEW
# ══════════════════════════════════════════════════════════════════════════════

class HomeView(View):
    def get(self, request):
        # Try high trust listings first
        featured = list(
            Listing.objects(
                is_available=True,
                ).order_by('-created_at').limit(6)
                )
# If not enough, get any available listings
        if len(featured) < 3:
            featured = list(
                Listing.objects(
                    is_available=True,
                    ).order_by('-id').limit(6)
                    )

        latest = list(
            Listing.objects(
                is_available=True,
                is_scam_flagged=False,
            ).order_by('-created_at').limit(3)
        )

        stats = {
            'total_listings':    Listing.objects(is_available=True).count(),
            'verified_listings': Listing.objects(
                is_available=True,
                trust_info__id_verified=True
            ).count(),
        }

        # Always return JSON — React frontend handles the UI
        from apps.listings.api_views import _listing_to_dict
        return JsonResponse({
            'listings': [_listing_to_dict(l) for l in featured],
            'latest':   [_listing_to_dict(l) for l in latest],
            'stats':    stats,
        })


# ══════════════════════════════════════════════════════════════════════════════
# SEARCH VIEW
# ══════════════════════════════════════════════════════════════════════════════

class SearchView(View):
    def get(self, request):
        from apps.listings.api_views import _listing_to_dict

        q = request.GET

        # ── Build filters ──────────────────────────────────────────
        filters = {'is_available': True}

        city      = q.get('city',     '').strip()
        locality  = q.get('locality', '').strip()
        ltype     = q.get('type',     '').strip()
        min_rent  = q.get('min_rent', '').strip()
        max_rent  = q.get('max_rent', '').strip()
        bedrooms  = q.get('bedrooms', '').strip()
        furnished = q.get('furnished','').strip()
        trust_min = q.get('trust_min','').strip()
        student   = q.get('student_only','').strip()
        pets      = q.get('pets',    '').strip()
        sort_by   = q.get('sort',    'newest')

        if city:
            filters['location__city__icontains'] = city
        if locality:
            filters['location__locality__icontains'] = locality
        if ltype:
            filters['listing_type'] = ltype
        if min_rent.isdigit():
            filters['rent__gte'] = int(min_rent)
        if max_rent.isdigit():
            filters['rent__lte'] = int(max_rent)
        if bedrooms.isdigit():
            filters['bedrooms'] = int(bedrooms)
        if furnished:
            filters['furnished'] = furnished
        if trust_min.isdigit() and int(trust_min) > 0:
            filters['trust_info__score__gte'] = int(trust_min)
        if student == 'on':
            filters['is_student_only'] = True
        if pets == 'on':
            filters['pets_allowed'] = True

        sort_map = {
            'newest':    '-created_at',
            'rent_asc':  'rent',
            'rent_desc': '-rent',
            'trust':     '-trust_info__score',
            'popular':   '-views_count',
        }
        sort_field = sort_map.get(sort_by, '-created_at')

        page     = max(1, int(q.get('page', 1)))
        per_page = int(q.get('limit', 12))
        offset   = (page - 1) * per_page

        try:
            qs    = Listing.objects(**filters).order_by(sort_field)
            total = qs.count()
            items = list(qs.skip(offset).limit(per_page))
        except Exception as e:
            # If filter fails, return all listings
            qs    = Listing.objects(is_available=True).order_by(sort_field)
            total = qs.count()
            items = list(qs.skip(offset).limit(per_page))

        return JsonResponse({
            'listings':    [_listing_to_dict(l) for l in items],
            'total':       total,
            'page':        page,
            'total_pages': max(1, math.ceil(total / per_page)),
        })



# ══════════════════════════════════════════════════════════════════════════════
# MAP SEARCH VIEW (Feature 4)
# ══════════════════════════════════════════════════════════════════════════════

class MapSearchView(View):
    def get(self, request):
        city = request.GET.get('city', 'Mumbai').strip()

        listings = Listing.objects(
            is_available=True,
            is_scam_flagged=False,
            location__city__icontains=city,
        ).limit(100)

        # ── Build GeoJSON for Leaflet ──────────────────────────────────────────
        features = []
        for l in listings:
            if l.location and l.location.latitude and l.location.longitude:
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type':        'Point',
                        'coordinates': [l.location.longitude, l.location.latitude],
                    },
                    'properties': {
                        'id':         str(l.id),
                        'title':      l.title,
                        'rent':       l.rent,
                        'type':       l.listing_type,
                        'bedrooms':   l.bedrooms,
                        'trust':      l.trust_info.score if l.trust_info else 0,
                        'is_scam':    l.is_scam_flagged,
                        'thumb':      l.photos[0] if l.photos else '/static/images/placeholder.jpg',
                        'url':        l.get_absolute_url(),
                        'locality':   l.location.locality if l.location else '',
                        'furnished':  l.furnished,
                    },
                })

        context = {
            'geojson':  json.dumps({'type': 'FeatureCollection', 'features': features}),
            'city':     city,
            'total':    len(features),
            'cities':   ['Mumbai', 'Pune', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai'],
        }
        from apps.listings.api_views import _listing_to_dict
        return JsonResponse({
            'listings': [_listing_to_dict(l) for l in listings],
            'total':    len(list(listings)),
            'city':     city,
        })

# ══════════════════════════════════════════════════════════════════════════════
# LISTING DETAIL VIEW
# ══════════════════════════════════════════════════════════════════════════════

class ListingDetailView(View):
    def get(self, request, listing_id):
        try:
            listing = Listing.objects.get(id=listing_id)
        except (Listing.DoesNotExist, Exception):
            messages.error(request, 'Listing not found.')
            return redirect('home')

        # ── Increment View Count ───────────────────────────────────────────────
        listing.update(inc__views_count=1)

        # ── AI Price Analysis (Feature 3) ──────────────────────────────────────
        price_data = estimate_price({
            'city':         listing.location.city     if listing.location else '',
            'locality':     listing.location.locality if listing.location else '',
            'listing_type': listing.listing_type,
            'bedrooms':     listing.bedrooms,
            'rent':         listing.rent,
        })

        # ── Scam Detection (Feature 7) ─────────────────────────────────────────
        owner_dict = {
            'id_verified':      listing.owner.id_verified if listing.owner else False,
            'account_age_days': listing.owner.account_age_days() if listing.owner else 0,
        }
        scam_data = detect_scam(
            listing={
                'photos':      listing.photos,
                'trust_info':  {
                    'bill_uploaded': listing.trust_info.bill_uploaded if listing.trust_info else False
                },
            },
            owner=owner_dict,
            price_analysis=price_data,
        )

        # ── Reviews ────────────────────────────────────────────────────────────
        reviews = list(
            Review.objects(listing=listing).order_by('-created_at').limit(10)
        )

        # ── Is Saved (by current user) ─────────────────────────────────────────
        is_saved = False
        if request.user.is_authenticated:
            mongo_user = get_mongo_user(request.user)
            if mongo_user:
                is_saved = bool(
                    SavedListing.objects(user=mongo_user, listing=listing).first()
                )

        # ── Similar Listings ───────────────────────────────────────────────────
        similar = list(
            Listing.objects(
                is_available=True,
                listing_type=listing.listing_type,
                location__city=listing.location.city if listing.location else '',
                id__ne=listing.id,
            ).order_by('-trust_info__score').limit(3)
        )

        context = {
            'listing':    listing,
            'price_data': price_data,
            'scam_data':  scam_data,
            'reviews':    reviews,
            'env_score':  listing.environment_score,
            'trust_info': listing.trust_info,
            'is_saved':   is_saved,
            'similar':    similar,
        }
        if request.headers.get('Accept') == 'application/json':
            data = _listing_to_dict(listing)
            data['price_data'] = price_data
            data['scam_data']  = scam_data
            return JsonResponse(data)
        from apps.listings.api_views import _listing_to_dict
        data = _listing_to_dict(listing)
        data['price_data'] = price_data
        data['scam_data']  = scam_data
        return JsonResponse(data)

# ══════════════════════════════════════════════════════════════════════════════
# CREATE LISTING VIEW
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class CreateListingView(View):
    def get(self, request):
        return JsonResponse({'message': 'Use POST to create a listing'})

    def post(self, request):
        data  = request.POST
        files = request.FILES.getlist('photos')

        mongo_user = get_mongo_user(request.user)
        if not mongo_user:
            messages.error(request, 'User not found. Please log in again.')
            return redirect('login')

        # ── Validate required fields ───────────────────────────────────────────
        title = data.get('title', '').strip()
        rent  = data.get('rent', '').strip()
        city  = data.get('city', '').strip()

        if not title:
            messages.error(request, 'Title is required.')
            return redirect('create_listing')
        if not rent.isdigit():
            messages.error(request, 'Please enter a valid rent amount.')
            return redirect('create_listing')
        if not city:
            messages.error(request, 'City is required.')
            return redirect('create_listing')

        # ── Build GeoLocation ──────────────────────────────────────────────────
        location = GeoLocation(
            city      = city,
            locality  = data.get('locality', ''),
            address   = data.get('address', ''),
            pincode   = data.get('pincode', ''),
            landmark  = data.get('landmark', ''),
            latitude  = float(data.get('latitude')  or 0) or None,
            longitude = float(data.get('longitude') or 0) or None,
        )

        # ── Build TrustInfo ────────────────────────────────────────────────────
        trust = TrustInfo(
            id_verified       = mongo_user.id_verified,
            bill_uploaded     = bool(data.get('utility_bill_confirmed')),
            video_walkthrough = bool(data.get('video_tour_url', '').strip()),
        )
        trust.score = _compute_trust_score(trust)

        # ── Build Environment Score (basic, from form) ─────────────────────────
        env = EnvironmentScore(
            safety_score = float(data.get('safety_score') or 5),
            noise_level  = data.get('noise_level', 'medium'),
            air_quality  = data.get('air_quality', 'good'),
            walkability  = float(data.get('walkability') or 5),
        )

        # Parse nearby amenities from form (comma-separated JSON)
        nearby_raw = data.get('nearby_amenities', '')
        if nearby_raw:
            try:
                nearby_list = json.loads(nearby_raw)
                for item in nearby_list:
                    env.nearby.append(NearbyAmenity(
                        name     = item.get('name', ''),
                        distance = float(item.get('distance', 0)),
                        icon     = item.get('icon', '📍'),
                        category = item.get('category', 'other'),
                    ))
            except Exception:
                pass

        # ── Create Listing ─────────────────────────────────────────────────────
        listing = Listing(
            owner          = mongo_user,
            title          = title,
            description    = data.get('description', ''),
            rent           = int(rent),
            deposit        = int(data.get('deposit') or 0),
            maintenance    = int(data.get('maintenance') or 0),
            is_negotiable  = data.get('is_negotiable') == 'on',
            listing_type   = data.get('listing_type', 'apartment'),
            is_commercial  = data.get('listing_type', 'apartment') in [
                        'shop', 'office', 'warehouse',
                        'showroom', 'coworking', 'studio_space',
                        'event_hall', 'garage', 'farmhouse', 'plot'
                        ],
            carpet_area    = int(data.get('carpet_area') or 0) or None,
            frontage       = float(data.get('frontage') or 0) or None,
            commercial_floor = data.get('commercial_floor', 'ground'),
            seating_capacity = int(data.get('seating_capacity') or 0) or None,
            ceiling_height   = float(data.get('ceiling_height') or 0) or None,
            lease_type       = data.get('lease_type', 'monthly'),
            lockin_months    = int(data.get('lockin_period') or 0),
            permitted_uses   = data.getlist('permitted_use'),
            rental_period  = data.get('rental_period', 'monthly'),
            min_stay_months= int(data.get('min_stay_months') or 1),
            bedrooms       = int(data.get('bedrooms') or 1),
            bathrooms      = int(data.get('bathrooms') or 1),
            area_sqft      = int(data.get('area_sqft') or 0) or None,
            floor_number   = int(data.get('floor_number') or 0),
            total_floors   = int(data.get('total_floors') or 1),
            furnished      = data.get('furnished', 'semi'),
            facing         = data.get('facing', 'east'),
            amenities      = data.getlist('amenities'),
            pets_allowed       = data.get('pets_allowed') == 'on',
            smoking_allowed    = data.get('smoking_allowed') == 'on',
            bachelors_allowed  = data.get('bachelors_allowed') == 'on',
            target_gender      = data.get('target_gender', 'any'),
            is_student_only    = data.get('is_student_only') == 'on',
            near_college       = data.get('near_college', ''),
            college_distance   = int(data.get('college_distance') or 0) or None,
            video_tour_url     = data.get('video_tour_url', ''),
            tour_360_url       = data.get('tour_360_url', ''),
            location           = location,
            trust_info         = trust,
            environment_score  = env,
        )
        listing.save()

        # ── Save Photos ────────────────────────────────────────────────────────
        if files:
            photo_urls    = _save_photos(files, str(listing.id))
            listing.update(photos=photo_urls)

        # ── Run AI Price Analysis ──────────────────────────────────────────────
        price_data = estimate_price({
            'city':         city,
            'locality':     data.get('locality', ''),
            'listing_type': data.get('listing_type', 'apartment'),
            'bedrooms':     int(data.get('bedrooms') or 1),
            'rent':         int(rent),
        })
        listing.update(
            market_price   = price_data.get('market_rent') or 0,
            price_verdict  = price_data.get('verdict', 'unknown'),
            price_diff_pct = price_data.get('difference_pct') or 0.0,
        )

        # ── Run Scam Detection ─────────────────────────────────────────────────
        scam_data = detect_scam(
            listing={
                'photos':     listing.photos,
                'trust_info': {'bill_uploaded': trust.bill_uploaded},
            },
            owner={
                'id_verified':      mongo_user.id_verified,
                'account_age_days': mongo_user.account_age_days(),
            },
            price_analysis=price_data,
        )
        listing.update(
            is_scam_flagged = scam_data['is_scam'],
            scam_risk_score = scam_data['risk_score'],
            scam_reasons    = scam_data['reasons'],
        )

        messages.success(request, '✅ Listing created successfully!')
        return JsonResponse({
            'id':      str(listing.id),
            'message': 'Listing created successfully',
        }, status=201)


# ══════════════════════════════════════════════════════════════════════════════
# EDIT LISTING VIEW
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class EditListingView(View):
    def get(self, request, listing_id):
        try:
            listing = Listing.objects.get(id=listing_id)
        except Exception:
            messages.error(request, 'Listing not found.')
            return redirect('profile')

        # Only owner can edit
        mongo_user = get_mongo_user(request.user)
        if str(listing.owner.id) != str(mongo_user.id):
            messages.error(request, '❌ You can only edit your own listings.')
            return redirect('profile')

        return render(request, 'listings/edit.html', {
            'listing': listing,
            'amenity_options': [
                'wifi', 'ac', 'parking', 'gym', 'lift', 'geyser',
                'washing_machine', 'fridge', 'tv', 'gas',
                'security', 'cctv', 'garden', 'terrace',
            ],
        })

    def post(self, request, listing_id):
        try:
            listing = Listing.objects.get(id=listing_id)
        except Exception:
            messages.error(request, 'Listing not found.')
            return redirect('profile')

        mongo_user = get_mongo_user(request.user)
        if str(listing.owner.id) != str(mongo_user.id):
            messages.error(request, '❌ Permission denied.')
            return redirect('profile')

        data = request.POST

        # Update fields
        listing.update(
            title          = data.get('title', listing.title),
            description    = data.get('description', listing.description),
            rent           = int(data.get('rent') or listing.rent),
            deposit        = int(data.get('deposit') or listing.deposit),
            is_negotiable  = data.get('is_negotiable') == 'on',
            furnished      = data.get('furnished', listing.furnished),
            amenities      = data.getlist('amenities'),
            pets_allowed   = data.get('pets_allowed') == 'on',
            smoking_allowed= data.get('smoking_allowed') == 'on',
            video_tour_url = data.get('video_tour_url', listing.video_tour_url),
            is_available   = data.get('is_available') == 'on',
            updated_at     = datetime.utcnow(),
        )

        # Handle new photos
        new_files = request.FILES.getlist('photos')
        if new_files:
            new_urls     = _save_photos(new_files, listing_id)
            current_urls = listing.photos or []
            listing.update(photos=current_urls + new_urls)

        # Re-run price analysis if rent changed
        refreshed  = Listing.objects.get(id=listing_id)
        price_data = estimate_price({
            'city':         refreshed.location.city if refreshed.location else '',
            'locality':     refreshed.location.locality if refreshed.location else '',
            'listing_type': refreshed.listing_type,
            'bedrooms':     refreshed.bedrooms,
            'rent':         refreshed.rent,
        })
        refreshed.update(
            market_price  = price_data.get('market_rent') or 0,
            price_verdict = price_data.get('verdict', 'unknown'),
        )

        messages.success(request, '✅ Listing updated successfully!')
        return redirect('listing_detail', listing_id=listing_id)


# ══════════════════════════════════════════════════════════════════════════════
# DELETE LISTING VIEW
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class DeleteListingView(View):
    def post(self, request, listing_id):
        try:
            listing = Listing.objects.get(id=listing_id)
        except Exception:
            messages.error(request, 'Listing not found.')
            return redirect('profile')

        mongo_user = get_mongo_user(request.user)
        if str(listing.owner.id) != str(mongo_user.id):
            messages.error(request, '❌ You can only delete your own listings.')
            return redirect('profile')

        listing.delete()
        messages.success(request, '✅ Listing deleted.')
        return redirect('profile')


# ══════════════════════════════════════════════════════════════════════════════
# SAVE / UNSAVE LISTING
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def toggle_save_listing(request, listing_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    mongo_user = get_mongo_user(request.user)
    try:
        listing = Listing.objects.get(id=listing_id)
    except Exception:
        return JsonResponse({'error': 'Not found'}, status=404)

    existing = SavedListing.objects(user=mongo_user, listing=listing).first()
    if existing:
        existing.delete()
        listing.update(dec__saves_count=1)
        return JsonResponse({'saved': False, 'message': 'Removed from saved'})
    else:
        SavedListing(user=mongo_user, listing=listing).save()
        listing.update(inc__saves_count=1)
        return JsonResponse({'saved': True, 'message': 'Saved successfully'})


# ══════════════════════════════════════════════════════════════════════════════
# SUBMIT REVIEW
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def submit_review(request, listing_id):
    if request.method != 'POST':
        return redirect('listing_detail', listing_id=listing_id)

    mongo_user = get_mongo_user(request.user)
    try:
        listing = Listing.objects.get(id=listing_id)
    except Exception:
        messages.error(request, 'Listing not found.')
        return redirect('home')

    # One review per user per listing
    existing = Review.objects(listing=listing, reviewer=mongo_user).first()
    if existing:
        messages.warning(request, 'You have already reviewed this listing.')
        return redirect('listing_detail', listing_id=listing_id)

    rating = int(request.POST.get('rating', 0))
    if not 1 <= rating <= 5:
        messages.error(request, 'Invalid rating.')
        return redirect('listing_detail', listing_id=listing_id)

    review = Review(
        listing               = listing,
        reviewer              = mongo_user,
        rating                = rating,
        comment               = request.POST.get('comment', ''),
        cleanliness_rating    = int(request.POST.get('cleanliness_rating') or rating),
        owner_rating          = int(request.POST.get('owner_rating') or rating),
        value_rating          = int(request.POST.get('value_rating') or rating),
        location_rating       = int(request.POST.get('location_rating') or rating),
    )
    review.save()

    # Update listing trust info
    all_reviews = Review.objects(listing=listing)
    count       = all_reviews.count()
    avg         = sum(r.rating for r in all_reviews) / count if count else 0

    listing.trust_info.reviews_count = count
    listing.trust_info.avg_rating    = round(avg, 1)
    listing.trust_info.score         = _compute_trust_score(listing.trust_info)
    listing.save()

    messages.success(request, '✅ Review submitted. Thank you!')
    return redirect('listing_detail', listing_id=listing_id)