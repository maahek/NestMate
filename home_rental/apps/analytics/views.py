"""
NestMate — Analytics Views
Covers:
  - Market Price Dashboard   (Feature 3 — AI Price Estimator data)
  - Environment Score View   (Feature 5 — Area Environment Scores)
  - Platform Stats Dashboard (admin overview)
  - City Insights            (per-city rental trends)
  - Trust Score Leaderboard  (Feature 2 — verified listings)
  - Scam Report Dashboard    (Feature 7 — flagged listings)
  - Price Heatmap Data       (JSON for map visualisation)
  - Search Trends            (what users are searching)
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View

from apps.listings.models import (
    Listing,
    Review,
    MarketPriceData,
    RoommateProfile,
    RoommateMatch,
    ChatRoom,
    RentalAgreement,
)
from apps.accounts.models import User
from ml.price_estimator import estimate_price, SEED_MARKET_DATA


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_mongo_user(django_user):
    """Resolve Django session user → MongoEngine User by email."""
    return User.objects(email=django_user.email).first()


def _is_admin(django_user):
    """Return True if the Django user is a superuser or staff."""
    return django_user.is_staff or django_user.is_superuser


def _month_label(dt: datetime) -> str:
    """Convert datetime to short month label e.g. 'Jan 24'."""
    return dt.strftime('%b %y')


def _price_range_label(rent: int) -> str:
    """Bucket a rent value into a human-readable range."""
    if rent < 5000:   return 'Under ₹5k'
    if rent < 10000:  return '₹5k–10k'
    if rent < 15000:  return '₹10k–15k'
    if rent < 25000:  return '₹15k–25k'
    if rent < 40000:  return '₹25k–40k'
    return '₹40k+'


def _get_platform_counts() -> dict:
    """
    Gather top-level platform statistics.
    Used by multiple views.
    """
    total_listings    = Listing.objects.count()
    available         = Listing.objects(is_available=True).count()
    verified          = Listing.objects(trust_info__id_verified=True).count()
    scam_flagged      = Listing.objects(is_scam_flagged=True).count()
    total_users       = User.objects.count()
    id_verified_users = User.objects(id_verified=True).count()
    total_reviews     = Review.objects.count()
    total_agreements  = RentalAgreement.objects.count()
    active_agreements = RentalAgreement.objects(status='active').count()
    total_chats       = ChatRoom.objects.count()
    deal_chats        = ChatRoom.objects(status='deal_done').count()
    roommate_profiles = RoommateProfile.objects(is_looking=True).count()
    roommate_matches  = RoommateMatch.objects.count()

    return {
        'total_listings':    total_listings,
        'available':         available,
        'verified':          verified,
        'scam_flagged':      scam_flagged,
        'total_users':       total_users,
        'id_verified_users': id_verified_users,
        'total_reviews':     total_reviews,
        'total_agreements':  total_agreements,
        'active_agreements': active_agreements,
        'total_chats':       total_chats,
        'deal_chats':        deal_chats,
        'roommate_profiles': roommate_profiles,
        'roommate_matches':  roommate_matches,
        'deal_rate':         round(
            (deal_chats / total_chats * 100) if total_chats else 0, 1
        ),
        'verification_rate': round(
            (verified / total_listings * 100) if total_listings else 0, 1
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 1. PLATFORM STATS DASHBOARD (Admin Only)
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class PlatformStatsView(View):
    """
    Admin-only dashboard showing overall platform health.
    Includes: listing counts, user growth, deal rate,
              scam flag rate, verification rate.
    """

    def get(self, request):
        if not _is_admin(request.user):
            messages.error(request, '❌ Admin access required.')
            return redirect('home')

        counts = _get_platform_counts()

        # ── Listings by city ───────────────────────────────────────────────────
        cities = [
            'Mumbai', 'Pune', 'Bangalore',
            'Delhi', 'Hyderabad', 'Chennai',
            'Kolkata', 'Ahmedabad'
        ]
        city_data = []
        for city in cities:
            total = Listing.objects(
                location__city__icontains=city
            ).count()
            verified = Listing.objects(
                location__city__icontains=city,
                trust_info__id_verified=True,
            ).count()
            scam = Listing.objects(
                location__city__icontains=city,
                is_scam_flagged=True,
            ).count()
            avg_rent_qs = list(
                Listing.objects(
                    location__city__icontains=city,
                    is_available=True,
                ).only('rent')
            )
            avg_rent = (
                round(sum(l.rent for l in avg_rent_qs) / len(avg_rent_qs))
                if avg_rent_qs else 0
            )
            city_data.append({
                'city':     city,
                'total':    total,
                'verified': verified,
                'scam':     scam,
                'avg_rent': avg_rent,
            })

        # ── Listings by type ───────────────────────────────────────────────────
        listing_types = ['apartment', 'house', 'pg', 'shared_room', 'studio', 'villa']
        type_data = []
        for ltype in listing_types:
            count = Listing.objects(listing_type=ltype).count()
            type_data.append({'type': ltype.replace('_', ' ').title(), 'count': count})

        # ── Listings created per month (last 6 months) ─────────────────────────
        monthly_data = []
        for i in range(5, -1, -1):
            dt    = datetime.utcnow() - timedelta(days=30 * i)
            start = dt.replace(day=1, hour=0, minute=0, second=0)
            if dt.month == 12:
                end = dt.replace(year=dt.year + 1, month=1, day=1)
            else:
                end = dt.replace(month=dt.month + 1, day=1)
            count = Listing.objects(
                created_at__gte=start,
                created_at__lt=end,
            ).count()
            monthly_data.append({
                'month': _month_label(dt),
                'count': count,
            })

        # ── Recent scam-flagged listings ───────────────────────────────────────
        scam_listings = list(
            Listing.objects(is_scam_flagged=True)
            .order_by('-created_at')
            .limit(5)
        )

        context = {
            'counts':        counts,
            'city_data':     city_data,
            'type_data':     type_data,
            'monthly_data':  monthly_data,
            'scam_listings': scam_listings,
            # JSON for charts
            'city_labels_json':  json.dumps([d['city'] for d in city_data]),
            'city_counts_json':  json.dumps([d['total'] for d in city_data]),
            'type_labels_json':  json.dumps([d['type'] for d in type_data]),
            'type_counts_json':  json.dumps([d['count'] for d in type_data]),
            'month_labels_json': json.dumps([d['month'] for d in monthly_data]),
            'month_counts_json': json.dumps([d['count'] for d in monthly_data]),
        }
        return render(request, 'analytics/platform_stats.html', context)


# ══════════════════════════════════════════════════════════════════════════════
# 2. MARKET PRICE DASHBOARD (Feature 3)
# ══════════════════════════════════════════════════════════════════════════════

class MarketPriceView(View):
    """
    Public dashboard showing market rent data by city and area.
    Lets anyone compare rents across localities.
    Also shows average rent trends and price distribution.
    Feature 3: AI Price Estimator backing data.
    """

    def get(self, request):
        selected_city = request.GET.get('city', 'Mumbai').strip()
        listing_type  = request.GET.get('type', 'apartment').strip()
        bedrooms      = int(request.GET.get('bedrooms', 1))

        # ── Market data from seed + MongoDB ────────────────────────────────────
        market_rows = []
        seen_localities = set()

        # From MongoDB MarketPriceData collection
        db_records = MarketPriceData.objects(
            city=selected_city.lower(),
            listing_type=listing_type,
            bedrooms=bedrooms,
        ).order_by('locality')

        for r in db_records:
            loc = r.locality.title()
            if loc not in seen_localities:
                seen_localities.add(loc)
                market_rows.append({
                    'locality':    loc,
                    'avg_rent':    r.avg_rent,
                    'min_rent':    r.min_rent or 0,
                    'max_rent':    r.max_rent or 0,
                    'data_points': r.data_points,
                    'source':      'database',
                })

        # Supplement with seed data
        for (city, locality, ltype, beds), avg_rent in SEED_MARKET_DATA.items():
            if (city == selected_city.lower() and
                    ltype == listing_type and
                    beds == bedrooms and
                    locality.title() not in seen_localities):
                seen_localities.add(locality.title())
                market_rows.append({
                    'locality':    locality.title(),
                    'avg_rent':    avg_rent,
                    'min_rent':    int(avg_rent * 0.75),
                    'max_rent':    int(avg_rent * 1.35),
                    'data_points': 0,
                    'source':      'estimated',
                })

        # Sort by avg_rent ascending
        market_rows.sort(key=lambda x: x['avg_rent'])

        # ── Live listings for this city ────────────────────────────────────────
        live_listings = list(
            Listing.objects(
                location__city__icontains=selected_city,
                listing_type=listing_type,
                bedrooms=bedrooms,
                is_available=True,
            ).order_by('rent').limit(50)
        )

        # Price distribution buckets
        price_buckets = defaultdict(int)
        for l in live_listings:
            price_buckets[_price_range_label(l.rent)] += 1

        bucket_order = [
            'Under ₹5k', '₹5k–10k', '₹10k–15k',
            '₹15k–25k', '₹25k–40k', '₹40k+'
        ]
        distribution = [
            {'label': b, 'count': price_buckets.get(b, 0)}
            for b in bucket_order
        ]

        # ── Summary stats from live listings ──────────────────────────────────
        rents = [l.rent for l in live_listings]
        stats = {}
        if rents:
            stats = {
                'avg':    round(sum(rents) / len(rents)),
                'min':    min(rents),
                'max':    max(rents),
                'median': sorted(rents)[len(rents) // 2],
                'count':  len(rents),
            }

        # ── Price estimator widget data ────────────────────────────────────────
        widget_result = None
        widget_rent   = request.GET.get('widget_rent', '').strip()
        if widget_rent.isdigit():
            widget_result = estimate_price({
                'city':         selected_city,
                'locality':     request.GET.get('widget_locality', '').strip(),
                'listing_type': listing_type,
                'bedrooms':     bedrooms,
                'rent':         int(widget_rent),
            })

        context = {
            'selected_city':  selected_city,
            'listing_type':   listing_type,
            'bedrooms':       bedrooms,
            'market_rows':    market_rows,
            'live_listings':  live_listings,
            'distribution':   distribution,
            'stats':          stats,
            'widget_result':  widget_result,
            'widget_rent':    widget_rent,
            'cities': [
                'Mumbai', 'Pune', 'Bangalore', 'Delhi',
                'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad'
            ],
            'listing_types': [
                'apartment', 'house', 'pg', 'shared_room', 'studio'
            ],
            # JSON for Chart.js
            'locality_labels_json': json.dumps(
                [r['locality'] for r in market_rows]
            ),
            'locality_rents_json':  json.dumps(
                [r['avg_rent'] for r in market_rows]
            ),
            'dist_labels_json': json.dumps(
                [d['label'] for d in distribution]
            ),
            'dist_counts_json': json.dumps(
                [d['count'] for d in distribution]
            ),
        }
        return render(request, 'analytics/market_price.html', context)


# ══════════════════════════════════════════════════════════════════════════════
# 3. ENVIRONMENT SCORE VIEW (Feature 5)
# ══════════════════════════════════════════════════════════════════════════════

class EnvironmentScoreView(View):
    """
    Public page showing environment scores by area.
    Lets users compare safety, noise, walkability across localities.
    Feature 5: House Environment Score backing data.
    """

    def get(self, request):
        selected_city = request.GET.get('city', 'Mumbai').strip()

        # ── Pull listings with environment scores ──────────────────────────────
        listings_with_env = list(
            Listing.objects(
                location__city__icontains=selected_city,
                is_available=True,
                is_scam_flagged=False,
            ).only(
                'title', 'location', 'rent',
                'environment_score', 'trust_info',
                'listing_type', 'photos',
            ).limit(100)
        )

        # ── Aggregate scores by locality ───────────────────────────────────────
        locality_scores = defaultdict(lambda: {
            'safety':      [],
            'walkability': [],
            'noise_low':   0,
            'noise_mid':   0,
            'noise_high':  0,
            'count':       0,
        })

        for l in listings_with_env:
            if not (l.location and l.location.locality):
                continue
            loc = l.location.locality.title()
            env = l.environment_score
            if not env:
                continue
            d = locality_scores[loc]
            if env.safety_score:
                d['safety'].append(env.safety_score)
            if env.walkability:
                d['walkability'].append(env.walkability)
            if env.noise_level == 'low':    d['noise_low']  += 1
            elif env.noise_level == 'high': d['noise_high'] += 1
            else:                           d['noise_mid']  += 1
            d['count'] += 1

        # ── Build summary rows ─────────────────────────────────────────────────
        env_rows = []
        for loc, d in locality_scores.items():
            if d['count'] == 0:
                continue
            avg_safety = round(
                sum(d['safety']) / len(d['safety']), 1
            ) if d['safety'] else 0
            avg_walk = round(
                sum(d['walkability']) / len(d['walkability']), 1
            ) if d['walkability'] else 0
            noise_label = (
                'Low'    if d['noise_low'] >= max(d['noise_mid'], d['noise_high'])
                else 'High' if d['noise_high'] >= max(d['noise_low'], d['noise_mid'])
                else 'Medium'
            )
            env_rows.append({
                'locality':    loc,
                'safety':      avg_safety,
                'walkability': avg_walk,
                'noise':       noise_label,
                'listings':    d['count'],
                'overall':     round((avg_safety + avg_walk) / 2, 1),
            })

        env_rows.sort(key=lambda x: x['overall'], reverse=True)

        # ── Best and worst areas ───────────────────────────────────────────────
        best_areas  = env_rows[:3]
        worst_areas = env_rows[-3:] if len(env_rows) >= 3 else []

        # ── Top listings by safety score ───────────────────────────────────────
        top_safe_listings = sorted(
            [
                l for l in listings_with_env
                if l.environment_score and l.environment_score.safety_score >= 7
            ],
            key=lambda l: l.environment_score.safety_score,
            reverse=True,
        )[:6]

        context = {
            'selected_city':    selected_city,
            'env_rows':         env_rows,
            'best_areas':       best_areas,
            'worst_areas':      worst_areas,
            'top_safe_listings': top_safe_listings,
            'cities': [
                'Mumbai', 'Pune', 'Bangalore', 'Delhi',
                'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad'
            ],
            # JSON for radar chart
            'env_locality_json': json.dumps(
                [r['locality'] for r in env_rows[:10]]
            ),
            'env_safety_json':   json.dumps(
                [r['safety']   for r in env_rows[:10]]
            ),
            'env_walk_json':     json.dumps(
                [r['walkability'] for r in env_rows[:10]]
            ),
        }
        return render(request, 'analytics/environment_score.html', context)


# ══════════════════════════════════════════════════════════════════════════════
# 4. CITY INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════

class CityInsightsView(View):
    """
    Deep-dive analytics for a single city.
    Shows: rent trends, locality breakdown, type distribution,
           trust score distribution, student rental options.
    """

    def get(self, request, city):
        city_display = city.title()

        # ── All listings for this city ─────────────────────────────────────────
        listings = list(
            Listing.objects(
                location__city__icontains=city,
            ).limit(500)
        )

        available = [l for l in listings if l.is_available]
        rents     = [l.rent for l in available]

        # ── Rent stats ─────────────────────────────────────────────────────────
        rent_stats = {}
        if rents:
            rent_stats = {
                'avg':    round(sum(rents) / len(rents)),
                'min':    min(rents),
                'max':    max(rents),
                'median': sorted(rents)[len(rents) // 2],
                'count':  len(rents),
            }

        # ── By locality ────────────────────────────────────────────────────────
        by_locality = defaultdict(list)
        for l in available:
            if l.location and l.location.locality:
                by_locality[l.location.locality.title()].append(l.rent)

        locality_rows = []
        for loc, loc_rents in by_locality.items():
            locality_rows.append({
                'locality': loc,
                'count':    len(loc_rents),
                'avg_rent': round(sum(loc_rents) / len(loc_rents)),
                'min_rent': min(loc_rents),
                'max_rent': max(loc_rents),
            })
        locality_rows.sort(key=lambda x: x['avg_rent'])

        # ── By listing type ────────────────────────────────────────────────────
        by_type = defaultdict(list)
        for l in available:
            by_type[l.listing_type].append(l.rent)

        type_rows = []
        for ltype, type_rents in by_type.items():
            type_rows.append({
                'type':     ltype.replace('_', ' ').title(),
                'count':    len(type_rents),
                'avg_rent': round(sum(type_rents) / len(type_rents)),
            })
        type_rows.sort(key=lambda x: x['count'], reverse=True)

        # ── Trust score distribution ───────────────────────────────────────────
        trust_buckets = {
            'Excellent (80–100)': 0,
            'Good (60–79)':       0,
            'Average (40–59)':    0,
            'Low (0–39)':         0,
        }
        for l in available:
            score = l.trust_info.score if l.trust_info else 0
            if score >= 80:   trust_buckets['Excellent (80–100)'] += 1
            elif score >= 60: trust_buckets['Good (60–79)']       += 1
            elif score >= 40: trust_buckets['Average (40–59)']    += 1
            else:             trust_buckets['Low (0–39)']         += 1

        # ── Price verdict breakdown ────────────────────────────────────────────
        verdict_counts = defaultdict(int)
        for l in available:
            verdict_counts[l.price_verdict or 'unknown'] += 1

        # ── Student rentals ────────────────────────────────────────────────────
        student_listings = [l for l in available if l.is_student_only]
        pg_listings      = [l for l in available if l.listing_type == 'pg']

        # ── Scam stats ─────────────────────────────────────────────────────────
        scam_count       = len([l for l in listings if l.is_scam_flagged])
        scam_rate        = round(scam_count / len(listings) * 100, 1) if listings else 0

        # ── Roommate seekers in this city ──────────────────────────────────────
        roommate_count = RoommateProfile.objects(
            city__icontains=city,
            is_looking=True,
        ).count()

        context = {
            'city':             city_display,
            'city_raw':         city,
            'total_listings':   len(listings),
            'available':        len(available),
            'rent_stats':       rent_stats,
            'locality_rows':    locality_rows,
            'type_rows':        type_rows,
            'trust_buckets':    trust_buckets,
            'verdict_counts':   dict(verdict_counts),
            'student_count':    len(student_listings),
            'pg_count':         len(pg_listings),
            'scam_count':       scam_count,
            'scam_rate':        scam_rate,
            'roommate_count':   roommate_count,
            # JSON for charts
            'locality_labels_json': json.dumps(
                [r['locality'] for r in locality_rows]
            ),
            'locality_avgs_json':   json.dumps(
                [r['avg_rent'] for r in locality_rows]
            ),
            'type_labels_json': json.dumps(
                [r['type'] for r in type_rows]
            ),
            'type_counts_json': json.dumps(
                [r['count'] for r in type_rows]
            ),
            'trust_labels_json': json.dumps(
                list(trust_buckets.keys())
            ),
            'trust_counts_json': json.dumps(
                list(trust_buckets.values())
            ),
        }
        return render(request, 'analytics/city_insights.html', context)


# ══════════════════════════════════════════════════════════════════════════════
# 5. TRUST SCORE LEADERBOARD (Feature 2)
# ══════════════════════════════════════════════════════════════════════════════

class TrustLeaderboardView(View):
    """
    Public leaderboard of highest-trust listings.
    Promotes verified listings and builds platform credibility.
    Feature 2: Verified Listings trust score showcase.
    """

    def get(self, request):
        city         = request.GET.get('city', '').strip()
        listing_type = request.GET.get('type', '').strip()

        filters = {
            'is_available':    True,
            'is_scam_flagged': False,
        }
        if city:         filters['location__city__icontains'] = city
        if listing_type: filters['listing_type'] = listing_type

        # ── Top 20 by trust score ──────────────────────────────────────────────
        top_listings = list(
            Listing.objects(**filters)
            .order_by('-trust_info__score')
            .limit(20)
        )

        # ── Trust score distribution across platform ───────────────────────────
        all_scores = [
            l.trust_info.score
            for l in Listing.objects(is_available=True).only('trust_info')
            if l.trust_info
        ]
        score_avg  = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
        score_pct_verified = round(
            sum(1 for s in all_scores if s >= 80) / len(all_scores) * 100, 1
        ) if all_scores else 0

        # ── Top verified owners ────────────────────────────────────────────────
        top_owners = list(
            User.objects(id_verified=True)
            .order_by('-trust_score')
            .limit(10)
        )

        context = {
            'top_listings':       top_listings,
            'score_avg':          score_avg,
            'score_pct_verified': score_pct_verified,
            'top_owners':         top_owners,
            'selected_city':      city,
            'selected_type':      listing_type,
            'cities': [
                'Mumbai', 'Pune', 'Bangalore', 'Delhi',
                'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad'
            ],
            'listing_types': [
                'apartment', 'house', 'pg', 'shared_room', 'studio'
            ],
        }
        return render(request, 'analytics/trust_leaderboard.html', context)


# ══════════════════════════════════════════════════════════════════════════════
# 6. SCAM REPORT DASHBOARD (Feature 7 — Admin Only)
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class ScamDashboardView(View):
    """
    Admin-only dashboard showing all scam-flagged listings.
    Shows risk scores, reasons, and allows admin review.
    Feature 7: Scam Detection system overview.
    """

    def get(self, request):
        if not _is_admin(request.user):
            messages.error(request, '❌ Admin access required.')
            return redirect('home')

        # ── All flagged listings ───────────────────────────────────────────────
        flagged = list(
            Listing.objects(is_scam_flagged=True)
            .order_by('-scam_risk_score', '-created_at')
        )

        # ── High risk (score >= 70) ────────────────────────────────────────────
        high_risk = [l for l in flagged if l.scam_risk_score >= 70]
        med_risk  = [l for l in flagged if 40 <= l.scam_risk_score < 70]
        low_risk  = [l for l in flagged if l.scam_risk_score < 40]

        # ── Reason frequency ───────────────────────────────────────────────────
        reason_counts = defaultdict(int)
        for l in flagged:
            for reason in (l.scam_reasons or []):
                reason_counts[reason] += 1

        reason_rows = sorted(
            reason_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # ── By city ────────────────────────────────────────────────────────────
        city_scam = defaultdict(int)
        for l in flagged:
            if l.location and l.location.city:
                city_scam[l.location.city] += 1

        context = {
            'flagged':      flagged,
            'high_risk':    high_risk,
            'med_risk':     med_risk,
            'low_risk':     low_risk,
            'total_flagged': len(flagged),
            'reason_rows':  reason_rows,
            'city_scam':    dict(city_scam),
        }
        return render(request, 'analytics/scam_dashboard.html', context)

    def post(self, request):
        """
        POST: Admin action on a flagged listing.
        Actions: unflag (clear scam flag) or remove (delete listing).
        """
        if not _is_admin(request.user):
            return JsonResponse({'error': 'Admin required'}, status=403)

        listing_id = request.POST.get('listing_id', '')
        action     = request.POST.get('action', '')

        try:
            listing = Listing.objects.get(id=listing_id)
        except Exception:
            messages.error(request, 'Listing not found.')
            return redirect('scam_dashboard')

        if action == 'unflag':
            listing.update(
                is_scam_flagged=False,
                scam_risk_score=0,
                scam_reasons=[],
            )
            messages.success(
                request,
                f'✅ Listing "{listing.title}" has been cleared.'
            )
        elif action == 'remove':
            listing.delete()
            messages.success(request, '✅ Listing removed from platform.')
        else:
            messages.error(request, 'Unknown action.')

        return redirect('scam_dashboard')


# ══════════════════════════════════════════════════════════════════════════════
# 7. PRICE HEATMAP DATA API (JSON — for map visualisation)
# ══════════════════════════════════════════════════════════════════════════════

class PriceHeatmapAPIView(View):
    """
    GET: Returns listing coordinates + rent for price heatmap.
    Used by the map page to colour-code pins by price.
    Params: city, type, bedrooms
    Response: { points: [{lat, lng, rent, trust, verdict}, ...] }
    """

    def get(self, request):
        city         = request.GET.get('city', 'Mumbai').strip()
        listing_type = request.GET.get('type', '').strip()
        bedrooms     = request.GET.get('bedrooms', '').strip()

        filters = {
            'is_available':    True,
            'is_scam_flagged': False,
            'location__city__icontains': city,
        }
        if listing_type:    filters['listing_type'] = listing_type
        if bedrooms.isdigit(): filters['bedrooms']  = int(bedrooms)

        listings = Listing.objects(**filters).limit(300)

        points = []
        for l in listings:
            if l.location and l.location.latitude and l.location.longitude:
                points.append({
                    'lat':     l.location.latitude,
                    'lng':     l.location.longitude,
                    'rent':    l.rent,
                    'trust':   l.trust_info.score if l.trust_info else 0,
                    'verdict': l.price_verdict or 'unknown',
                    'title':   l.title,
                    'id':      str(l.id),
                })

        # Compute rent min/max for normalisation in frontend
        rents   = [p['rent'] for p in points]
        rent_min = min(rents) if rents else 0
        rent_max = max(rents) if rents else 0

        return JsonResponse({
            'points':   points,
            'count':    len(points),
            'rent_min': rent_min,
            'rent_max': rent_max,
            'city':     city,
        })


# ══════════════════════════════════════════════════════════════════════════════
# 8. MARKET DATA API (JSON — for price estimator widget)
# ══════════════════════════════════════════════════════════════════════════════

class MarketDataAPIView(View):
    """
    GET: Returns market rent summary for a specific location.
    Used by the price estimator AJAX widget on listing pages.
    Params: city, locality, type, bedrooms
    Response: {
        avg_rent, min_rent, max_rent,
        data_points, verdict, label, confidence
    }
    """

    def get(self, request):
        q    = request.GET
        city = q.get('city', '').strip()
        loc  = q.get('locality', '').strip()
        ltype = q.get('type', 'apartment').strip()
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

        # Add price verdict if rent provided
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


# ══════════════════════════════════════════════════════════════════════════════
# 9. CITY STATS API (JSON — for landing page + roommate page)
# ══════════════════════════════════════════════════════════════════════════════

class CityStatsAPIView(View):
    """
    GET: Returns key stats for each city.
    Used by landing page hero and roommate landing page.
    Response: {
        stats: {
            Mumbai: { listings, avg_rent, verified_pct, roommate_seekers },
            ...
        }
    }
    """

    def get(self, request):
        cities = [
            'Mumbai', 'Pune', 'Bangalore', 'Delhi',
            'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad'
        ]
        stats = {}

        for city in cities:
            city_listings = list(
                Listing.objects(
                    location__city__icontains=city,
                    is_available=True,
                ).only('rent', 'trust_info')
            )
            rents = [l.rent for l in city_listings]
            verified_count = sum(
                1 for l in city_listings
                if l.trust_info and l.trust_info.id_verified
            )
            roommate_count = RoommateProfile.objects(
                city__icontains=city,
                is_looking=True,
            ).count()

            stats[city] = {
                'listings':         len(city_listings),
                'avg_rent':         round(sum(rents) / len(rents)) if rents else 0,
                'verified_pct':     round(
                    verified_count / len(city_listings) * 100, 1
                ) if city_listings else 0,
                'roommate_seekers': roommate_count,
            }

        return JsonResponse({'stats': stats})


# ══════════════════════════════════════════════════════════════════════════════
# 10. ADMIN: UNFLAG / VERIFY LISTING (Quick Action)
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class AdminListingActionView(View):
    """
    POST: Admin quick actions on any listing.
    Actions:
      - verify     → set trust_info.id_verified=True, recompute trust score
      - unflag     → clear scam flag
      - feature    → mark as featured
      - unfeature  → remove featured
      - remove     → delete listing
    """

    def post(self, request, listing_id):
        if not _is_admin(request.user):
            return JsonResponse({'error': 'Admin required'}, status=403)

        action = request.POST.get('action', '')

        try:
            listing = Listing.objects.get(id=listing_id)
        except Exception:
            messages.error(request, 'Listing not found.')
            return redirect('platform_stats')

        if action == 'verify':
            if listing.trust_info:
                listing.trust_info.id_verified = True
                listing.compute_trust_score()
                listing.save()
            messages.success(
                request,
                f'✅ "{listing.title}" is now verified.'
            )

        elif action == 'unflag':
            listing.update(
                is_scam_flagged=False,
                scam_risk_score=0,
                scam_reasons=[],
            )
            messages.success(
                request,
                f'✅ Scam flag removed from "{listing.title}".'
            )

        elif action == 'feature':
            listing.update(is_featured=True)
            messages.success(
                request,
                f'⭐ "{listing.title}" is now featured.'
            )

        elif action == 'unfeature':
            listing.update(is_featured=False)
            messages.success(
                request,
                f'✅ "{listing.title}" removed from featured.'
            )

        elif action == 'remove':
            title = listing.title
            listing.delete()
            messages.success(
                request,
                f'✅ Listing "{title}" removed from platform.'
            )

        else:
            messages.error(request, f'Unknown action: {action}')

        # Redirect back to the referring page
        next_url = request.POST.get('next', 'platform_stats')
        return redirect(next_url)