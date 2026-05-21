"""
NestMate — Listings API Views
Returns JSON for React frontend.
All endpoints used by the React app via Axios.
"""

import os
import math
import re
from datetime import datetime

from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings

from apps.listings.models import (
    Listing, Review, MarketPriceData,
    GeoLocation, TrustInfo, EnvironmentScore,
)
from apps.accounts.models import User
from ml.price_estimator import estimate_price, detect_scam, SEED_MARKET_DATA


# ══════════════════════════════════════════════════════════════════════════════
# HELPER — Convert Listing document → JSON dict
# Used by ALL listing API views
# ══════════════════════════════════════════════════════════════════════════════

def _listing_to_dict(l: Listing) -> dict:
    """
    Convert a MongoEngine Listing document into a
    plain Python dict that can be serialised to JSON.
    """
    return {
        # ── Core fields ───────────────────────────────────────────────────────
        'id':              str(l.id),
        'title':           l.title         or '',
        'description':     l.description   or '',
        'rent':            l.rent,
        'deposit':         l.deposit        or 0,
        'maintenance':     l.maintenance    or 0,
        'is_negotiable':   l.is_negotiable,
        'listing_type':    l.listing_type,
        'rental_period':   l.rental_period,
        'min_stay_months': l.min_stay_months or 1,

        # ── Property specs ────────────────────────────────────────────────────
        'bedrooms':        l.bedrooms,
        'bathrooms':       l.bathrooms,
        'area_sqft':       l.area_sqft,
        'floor_number':    l.floor_number  or 0,
        'total_floors':    l.total_floors  or 1,
        'furnished':       l.furnished,
        'facing':          l.facing        or '',
        'amenities':       l.amenities     or [],

        # ── Rules ─────────────────────────────────────────────────────────────
        'pets_allowed':       l.pets_allowed,
        'smoking_allowed':    l.smoking_allowed,
        'bachelors_allowed':  l.bachelors_allowed,
        'target_gender':      l.target_gender,
        'is_student_only':    l.is_student_only,
        'near_college':       l.near_college      or '',
        'college_distance':   l.college_distance,

        # ── Media ─────────────────────────────────────────────────────────────
        'photos':         l.photos          or [],
        'video_tour_url': l.video_tour_url  or '',
        'tour_360_url':   l.tour_360_url    or '',

        # ── Status ────────────────────────────────────────────────────────────
        'is_available':   l.is_available,
        'is_featured':    l.is_featured,
        'views_count':    l.views_count     or 0,
        'saves_count':    l.saves_count     or 0,
        'created_at':     l.created_at.isoformat() if l.created_at else '',
        'updated_at':     l.updated_at.isoformat() if l.updated_at else '',

        # ── AI fields ─────────────────────────────────────────────────────────
        'price_verdict':  l.price_verdict   or 'unknown',
        'market_price':   l.market_price    or 0,
        'price_diff_pct': l.price_diff_pct  or 0,
        'is_scam_flagged': l.is_scam_flagged,
        'scam_risk_score': l.scam_risk_score or 0,
        'scam_reasons':    l.scam_reasons    or [],

        # ── Trust Info ────────────────────────────────────────────────────────
        'trust_info': {
            'score':             l.trust_info.score             if l.trust_info else 0,
            'id_verified':       l.trust_info.id_verified       if l.trust_info else False,
            'bill_uploaded':     l.trust_info.bill_uploaded     if l.trust_info else False,
            'video_walkthrough': l.trust_info.video_walkthrough if l.trust_info else False,
            'reviews_count':     l.trust_info.reviews_count     if l.trust_info else 0,
            'avg_rating':        l.trust_info.avg_rating        if l.trust_info else 0.0,
        } if l.trust_info else None,

        # ── Location ──────────────────────────────────────────────────────────
        'location': {
            'city':      l.location.city      if l.location else '',
            'locality':  l.location.locality  if l.location else '',
            'address':   l.location.address   if l.location else '',
            'pincode':   l.location.pincode   if l.location else '',
            'landmark':  l.location.landmark  if l.location else '',
            'latitude':  l.location.latitude  if l.location else None,
            'longitude': l.location.longitude if l.location else None,
        } if l.location else None,

        # ── Environment Score ──────────────────────────────────────────────────
        'environment_score': {
            'safety_score': l.environment_score.safety_score if l.environment_score else 0,
            'walkability':  l.environment_score.walkability  if l.environment_score else 0,
            'noise_level':  l.environment_score.noise_level  if l.environment_score else 'medium',
            'air_quality':  l.environment_score.air_quality  if l.environment_score else 'good',
            'nearby': [
                {
                    'name':     n.name,
                    'distance': n.distance,
                    'icon':     n.icon,
                    'category': n.category,
                }
                for n in l.environment_score.nearby
            ] if l.environment_score and l.environment_score.nearby else [],
        } if l.environment_score else None,

        # ── Map shorthand (used by Leaflet MapView component) ─────────────────
        'lat':       l.location.latitude  if l.location else None,
        'lng':       l.location.longitude if l.location else None,
        'trust':     l.trust_info.score   if l.trust_info else 0,
        'type':      l.listing_type,
        'locality':  l.location.locality  if l.location else '',
        'thumb':     l.photos[0]          if l.photos else '',
        'is_scam':   l.is_scam_flagged,
        'is_student': l.is_student_only,
        'url':       f'/listing/{l.id}',
    }


def _get_mongo_user(django_user):
    """Resolve Django session user → MongoEngine User."""
    return User.objects(email=django_user.email).first()


# ══════════════════════════════════════════════════════════════════════════════
# 1. ALL LISTINGS — GET /api/listings/
# Used by: Home page, Search page, Map
# ══════════════════════════════════════════════════════════════════════════════

class ListingsAPIView(View):
    """
    GET /api/listings/
    Params: city, type, min_rent, max_rent, bedrooms,
            trust_min, student_only, pets, sort, page
    Returns: { listings, total, page, total_pages }
    """

    def get(self, request):
        q = request.GET

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
        page      = max(1, int(q.get('page',  1)))
        per_page  = int(q.get('limit', 12))

        # ── Start with base queryset ───────────────────────────────
        qs = Listing.objects(is_available=True)

        # ── Apply filters one by one safely ───────────────────────
        try:
            if city:
                qs = qs.filter(location__city__icontains=city)
        except Exception:
            pass

        try:
            if locality:
                qs = qs.filter(location__locality__icontains=locality)
        except Exception:
            pass

        try:
            if ltype:
                qs = qs.filter(listing_type=ltype)
        except Exception:
            pass

        try:
            if min_rent.isdigit():
                qs = qs.filter(rent__gte=int(min_rent))
        except Exception:
            pass

        try:
            if max_rent.isdigit():
                qs = qs.filter(rent__lte=int(max_rent))
        except Exception:
            pass

        try:
            if bedrooms.isdigit():
                qs = qs.filter(bedrooms=int(bedrooms))
        except Exception:
            pass

        try:
            if furnished:
                qs = qs.filter(furnished=furnished)
        except Exception:
            pass

        try:
            if trust_min.isdigit() and int(trust_min) > 0:
                qs = qs.filter(trust_info__score__gte=int(trust_min))
        except Exception:
            pass

        try:
            if student == 'on':
                qs = qs.filter(is_student_only=True)
        except Exception:
            pass

        try:
            if pets == 'on':
                qs = qs.filter(pets_allowed=True)
        except Exception:
            pass

        # ── Sort ──────────────────────────────────────────────────
        sort_map = {
            'newest':    '-created_at',
            'rent_asc':  'rent',
            'rent_desc': '-rent',
            'trust':     '-trust_info__score',
            'popular':   '-views_count',
        }
        sort_field = sort_map.get(sort_by, '-created_at')

        try:
            qs = qs.order_by(sort_field)
        except Exception:
            qs = qs.order_by('-id')

        # ── Paginate ──────────────────────────────────────────────
        import math
        offset = (page - 1) * per_page

        try:
            total = qs.count()
            items = list(qs.skip(offset).limit(per_page))
        except Exception:
            total = 0
            items = []

        return JsonResponse({
            'listings':    [_listing_to_dict(l) for l in items],
            'total':       total,
            'page':        page,
            'total_pages': max(1, math.ceil(total / per_page)),
            'has_next':    page < max(1, math.ceil(total / per_page)),
            'has_prev':    page > 1,
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
        return CreateListingAPIView().post(request)

    def post(self, request):
        """POST /api/listings/ — Create a new listing."""
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
        return CreateListingAPIView().post(request)


# ══════════════════════════════════════════════════════════════════════════════
# 2. SINGLE LISTING — GET /api/listings/<id>/
# ══════════════════════════════════════════════════════════════════════════════

class ListingDetailAPIView(View):
    """
    GET /api/listings/<listing_id>/
    Returns full listing data including AI analysis.
    """

    def get(self, request, listing_id):
        try:
            listing = Listing.objects.get(id=listing_id)
        except Exception:
            return JsonResponse({'error': 'Listing not found'}, status=404)

        # Increment views
        listing.update(inc__views_count=1)

        data = _listing_to_dict(listing)
        return JsonResponse(data)


# ══════════════════════════════════════════════════════════════════════════════
# 3. CREATE LISTING — POST /api/listings/create/
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class CreateListingAPIView(View):
    """
    POST /api/listings/create/
    Accepts multipart/form-data from React CreateListing page.
    """

    def post(self, request):
        mongo_user = _get_mongo_user(request.user)
        if not mongo_user:
            return JsonResponse({'error': 'User not found'}, status=404)

        data  = request.POST
        files = request.FILES.getlist('photos')

        # ── Validate required fields ───────────────────────────────────────────
        title = data.get('title', '').strip()
        rent  = data.get('rent',  '').strip()
        city  = data.get('city',  '').strip()

        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        if not rent.isdigit():
            return JsonResponse({'error': 'Valid rent amount is required'}, status=400)
        if not city:
            return JsonResponse({'error': 'City is required'}, status=400)

        # ── Build embedded documents ───────────────────────────────────────────
        location = GeoLocation(
            city      = city,
            locality  = data.get('locality', ''),
            address   = data.get('address',  ''),
            pincode   = data.get('pincode',  ''),
            latitude  = float(data.get('latitude')  or 0) or None,
            longitude = float(data.get('longitude') or 0) or None,
        )

        trust = TrustInfo(
    id_verified       = mongo_user.id_verified,
    bill_uploaded     = mongo_user.bill_verified or (data.get('utility_bill_confirmed') == 'true'),
    video_walkthrough = bool(data.get('video_tour_url', '')),
)

# Calculate trust score
        score = 0
        if trust.id_verified:       score += 40
        if trust.bill_uploaded:     score += 25
        if trust.video_walkthrough: score += 20
# Base score for having photos
        if len(data.getlist('photos')) > 0: score += 10
# Minimum score of 60 so listing always shows
        score = max(score, 60)
        trust.score = min(100, score)
         # Generate unique slug from title + timestamp
        import re
        import time
        raw_slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        unique_slug = f"{raw_slug}-{int(time.time())}"

        # ── Create Listing ─────────────────────────────────────────────────────
        listing = Listing(
            owner           = mongo_user,
            title           = title,
            slug           = unique_slug,
            description     = data.get('description', ''),
            rent            = int(rent),
            deposit         = int(data.get('deposit')     or 0),
            maintenance     = int(data.get('maintenance') or 0),
            listing_type    = data.get('listing_type',  'apartment'),
            rental_period   = data.get('rental_period', 'monthly'),
            min_stay_months = int(data.get('min_stay_months') or 1),
            bedrooms        = int(data.get('bedrooms')   or 1),
            bathrooms       = int(data.get('bathrooms')  or 1),
            area_sqft       = int(data.get('area_sqft')  or 0) or None,
            furnished       = data.get('furnished', 'semi'),
            amenities       = data.getlist('amenities'),
            pets_allowed    = data.get('pets_allowed')    == 'true',
            smoking_allowed = data.get('smoking_allowed') == 'true',
            is_negotiable   = data.get('is_negotiable')   != 'false',
            is_student_only = data.get('is_student_only') == 'true',
            near_college    = data.get('near_college', ''),
            video_tour_url  = data.get('video_tour_url', ''),
            tour_360_url    = data.get('tour_360_url',  ''),
            location        = location,
            trust_info      = trust,
        )
        listing.save()

        # ── Save uploaded photos ────────────────────────────────────────────────
        if files:
            urls = []
            upload_dir = os.path.join(
                settings.MEDIA_ROOT, 'listings', str(listing.id)
            )
            os.makedirs(upload_dir, exist_ok=True)
            for f in files:
                fname = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{f.name}"
                fpath = os.path.join(upload_dir, fname)
                with open(fpath, 'wb+') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)
                urls.append(f'/media/listings/{listing.id}/{fname}')
            listing.update(photos=urls)

        # ── Run AI price analysis ──────────────────────────────────────────────
        price_data = estimate_price({
            'city':         city,
            'locality':     data.get('locality', ''),
            'listing_type': data.get('listing_type', 'apartment'),
            'bedrooms':     int(data.get('bedrooms') or 1),
            'rent':         int(rent),
        })

        # ── Run scam detection ─────────────────────────────────────────────────
        scam_data = detect_scam(
            listing={
                'photos':     listing.photos or [],
                'trust_info': {'bill_uploaded': trust.bill_uploaded},
            },
            owner={
                'id_verified':      mongo_user.id_verified,
                'account_age_days': mongo_user.account_age_days(),
            },
            price_analysis=price_data,
        )

        listing.update(
            market_price    = price_data.get('market_rent') or 0,
            price_verdict   = price_data.get('verdict', 'unknown'),
            price_diff_pct  = price_data.get('difference_pct') or 0.0,
            is_scam_flagged = scam_data['is_scam'],
            scam_risk_score = scam_data['risk_score'],
            scam_reasons    = scam_data['reasons'],
        )

        return JsonResponse({
            'id':      str(listing.id),
            'message': 'Listing created successfully',
        }, status=201)


# ══════════════════════════════════════════════════════════════════════════════
# 4. PRICE CHECK — GET /api/listings/price-check/
# Used by: ListingDetail page, CreateListing live hint
# ══════════════════════════════════════════════════════════════════════════════

class PriceCheckAPIView(View):
    """
    GET /api/listings/price-check/
    Params: city, locality, type, bedrooms, rent
    Returns: { market_rent, verdict, label, difference_pct, explanation, confidence }
    """

    def get(self, request):
        q    = request.GET
        rent = q.get('rent', '0').strip()

        if not rent.lstrip('-').isdigit():
            return JsonResponse(
                {'error': 'Invalid rent value'},
                status=400
            )

        result = estimate_price({
            'city':         q.get('city',     '').strip(),
            'locality':     q.get('locality', '').strip(),
            'listing_type': q.get('type',     'apartment').strip(),
            'bedrooms':     int(q.get('bedrooms', 1)),
            'rent':         int(rent),
        })
        return JsonResponse(result)


# ══════════════════════════════════════════════════════════════════════════════
# 5. SCAM CHECK — GET /api/listings/scam-check/<id>/
# Used by: ListingDetail page
# ══════════════════════════════════════════════════════════════════════════════

class ScamCheckAPIView(View):
    """
    GET /api/listings/scam-check/<listing_id>/
    Returns: { is_scam, risk_score, reasons, badge, badge_class }
    """

    def get(self, request, listing_id):
        try:
            listing = Listing.objects.get(id=listing_id)
        except Exception:
            return JsonResponse({'error': 'Not found'}, status=404)

        price_data = estimate_price({
            'city':         listing.location.city     if listing.location else '',
            'locality':     listing.location.locality if listing.location else '',
            'listing_type': listing.listing_type,
            'bedrooms':     listing.bedrooms,
            'rent':         listing.rent,
        })

        owner_data = {
            'id_verified':      listing.owner.id_verified if listing.owner else False,
            'account_age_days': listing.owner.account_age_days() if listing.owner else 365,
        }

        result = detect_scam(
            listing={
                'photos':     listing.photos or [],
                'trust_info': {
                    'bill_uploaded': listing.trust_info.bill_uploaded
                    if listing.trust_info else False
                },
            },
            owner=owner_data,
            price_analysis=price_data,
        )
        return JsonResponse(result)


# ══════════════════════════════════════════════════════════════════════════════
# 6. NEARBY LISTINGS — GET /api/listings/nearby/
# Used by: Map page radius search
# ══════════════════════════════════════════════════════════════════════════════

class NearbyListingsAPIView(View):
    """
    GET /api/listings/nearby/
    Params: lat, lng, radius_km (default 2)
    Returns: { listings, count } — sorted by distance
    """

    def get(self, request):
        try:
            lat    = float(request.GET.get('lat', 0))
            lng    = float(request.GET.get('lng', 0))
            radius = float(request.GET.get('radius_km', 2))
        except (ValueError, TypeError):
            return JsonResponse(
                {'error': 'Invalid coordinates'},
                status=400
            )

        if lat == 0 and lng == 0:
            return JsonResponse(
                {'error': 'Coordinates required'},
                status=400
            )

        candidates = Listing.objects(
            is_available=True,
            is_scam_flagged=False,
        ).limit(500)

        def haversine(lat1, lng1, lat2, lng2):
            R    = 6371
            dlat = math.radians(lat2 - lat1)
            dlng = math.radians(lng2 - lng1)
            a    = (
                math.sin(dlat / 2) ** 2 +
                math.cos(math.radians(lat1)) *
                math.cos(math.radians(lat2)) *
                math.sin(dlng / 2) ** 2
            )
            return R * 2 * math.asin(math.sqrt(a))

        nearby = []
        for l in candidates:
            if l.location and l.location.latitude and l.location.longitude:
                dist = haversine(lat, lng, l.location.latitude, l.location.longitude)
                if dist <= radius:
                    d            = _listing_to_dict(l)
                    d['dist_km'] = round(dist, 2)
                    nearby.append(d)

        nearby.sort(key=lambda x: x['dist_km'])
        return JsonResponse({'listings': nearby, 'count': len(nearby)})


# ══════════════════════════════════════════════════════════════════════════════
# 7. MARKET DATA — GET /api/listings/market-data/
# Used by: Analytics page, price widget
# ══════════════════════════════════════════════════════════════════════════════

class MarketDataAPIView(View):
    """
    GET /api/listings/market-data/
    Params: city, locality, type, bedrooms, rent
    Returns: { avg_rent, min_rent, max_rent, verdict, label }
    """

    def get(self, request):
        q    = request.GET
        city = q.get('city',     '').strip().lower()
        loc  = q.get('locality', '').strip().lower()
        ltype = q.get('type',    'apartment').strip().lower()
        beds  = int(q.get('bedrooms', 1))
        rent  = int(q.get('rent', 0))

        # Try MongoDB first
        record = MarketPriceData.objects(
            city__iexact=city,
            locality__iexact=loc,
            listing_type=ltype,
            bedrooms=beds,
        ).first()

        if record:
            result = {
                'avg_rent':    record.avg_rent,
                'min_rent':    record.min_rent,
                'max_rent':    record.max_rent,
                'data_points': record.data_points,
                'source':      'database',
            }
        else:
            # Fall back to seed data via price estimator
            estimation = estimate_price({
                'city':         city,
                'locality':     loc,
                'listing_type': ltype,
                'bedrooms':     beds,
                'rent':         rent or 10000,
            })
            result = {
                'avg_rent':    estimation.get('market_rent'),
                'min_rent':    None,
                'max_rent':    None,
                'data_points': 0,
                'source':      'estimated',
            }

        # Add price verdict if rent was provided
        if rent and result.get('avg_rent'):
            avg    = result['avg_rent']
            diff   = round((rent - avg) / avg * 100, 1)
            if diff > 20:
                result['verdict'] = 'overpriced'
                result['label']   = f'{abs(diff):.0f}% overpriced'
            elif diff < -20:
                result['verdict'] = 'underpriced'
                result['label']   = f'{abs(diff):.0f}% below market'
            else:
                result['verdict'] = 'fair'
                result['label']   = 'Fair price'
            result['diff_pct'] = diff

        return JsonResponse(result)