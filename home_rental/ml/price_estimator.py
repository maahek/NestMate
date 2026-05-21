"""
NestMate — AI Price Estimator & Scam Detection Engine
Feature 3: Fair Rent Price Analysis
Feature 7: Suspicious Listing Detection

Price Estimator:
  Compares a listing's rent against market data (seed + MongoDB).
  Returns: verdict (fair/overpriced/underpriced), difference %, explanation.

Scam Detector:
  Applies rule-based scoring to flag suspicious listings.
  Rules: price too low, unverified owner, no photos, new account, etc.
  Returns: is_scam flag, risk score 0–100, list of reasons.
"""

from typing import Dict, List, Optional, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# SEED MARKET DATA
# (city, locality, listing_type, bedrooms) → average_rent_INR
#
# In production this is supplemented / overridden by
# the MarketPriceData MongoDB collection (populated from
# Kaggle datasets, web scraping, or manual admin entry).
# ══════════════════════════════════════════════════════════════════════════════

SEED_MARKET_DATA: Dict[Tuple, int] = {

    # ── Mumbai ─────────────────────────────────────────────────────────────────
    ('mumbai', 'andheri',        'apartment', 1): 25000,
    ('mumbai', 'andheri',        'apartment', 2): 42000,
    ('mumbai', 'andheri',        'apartment', 3): 65000,
    ('mumbai', 'andheri',        'pg',        1):  9000,
    ('mumbai', 'bandra',         'apartment', 1): 38000,
    ('mumbai', 'bandra',         'apartment', 2): 65000,
    ('mumbai', 'bandra',         'house',     3): 95000,
    ('mumbai', 'borivali',       'apartment', 1): 18000,
    ('mumbai', 'borivali',       'apartment', 2): 30000,
    ('mumbai', 'borivali',       'pg',        1):  7500,
    ('mumbai', 'thane',          'apartment', 1): 14000,
    ('mumbai', 'thane',          'apartment', 2): 22000,
    ('mumbai', 'navi mumbai',    'apartment', 1): 13000,
    ('mumbai', 'navi mumbai',    'apartment', 2): 20000,
    ('mumbai', 'dadar',          'apartment', 1): 28000,
    ('mumbai', 'malad',          'apartment', 1): 19000,
    ('mumbai', 'goregaon',       'apartment', 1): 21000,
    ('mumbai', 'powai',          'apartment', 1): 27000,
    ('mumbai', 'powai',          'apartment', 2): 45000,
    ('mumbai', 'kandivali',      'apartment', 1): 17000,
    ('mumbai', 'lower parel',    'apartment', 1): 40000,
    ('mumbai', 'lower parel',    'apartment', 2): 70000,
    ('mumbai', 'worli',          'apartment', 1): 50000,
    ('mumbai', 'colaba',         'apartment', 1): 45000,

    # ── Pune ──────────────────────────────────────────────────────────────────
    ('pune', 'koregaon park',    'apartment', 1): 16000,
    ('pune', 'koregaon park',    'apartment', 2): 27000,
    ('pune', 'koregaon park',    'pg',        1):  7000,
    ('pune', 'wakad',            'apartment', 1): 12000,
    ('pune', 'wakad',            'apartment', 2): 19000,
    ('pune', 'wakad',            'pg',        1):  6000,
    ('pune', 'hinjewadi',        'apartment', 1): 11000,
    ('pune', 'hinjewadi',        'apartment', 2): 17500,
    ('pune', 'baner',            'apartment', 1): 13000,
    ('pune', 'baner',            'apartment', 2): 21000,
    ('pune', 'kothrud',          'apartment', 1): 12000,
    ('pune', 'kothrud',          'apartment', 2): 18000,
    ('pune', 'viman nagar',      'apartment', 1): 14000,
    ('pune', 'viman nagar',      'apartment', 2): 22000,
    ('pune', 'hadapsar',         'apartment', 1):  9000,
    ('pune', 'hadapsar',         'apartment', 2): 14000,
    ('pune', 'shivajinagar',     'apartment', 1): 15000,
    ('pune', 'kalyani nagar',    'apartment', 1): 15000,
    ('pune', 'pimpri',           'apartment', 1):  9500,
    ('pune', 'chinchwad',        'apartment', 1):  9000,

    # ── Bangalore ─────────────────────────────────────────────────────────────
    ('bangalore', 'koramangala',  'apartment', 1): 22000,
    ('bangalore', 'koramangala',  'apartment', 2): 38000,
    ('bangalore', 'koramangala',  'pg',        1):  9500,
    ('bangalore', 'indiranagar',  'apartment', 1): 24000,
    ('bangalore', 'indiranagar',  'apartment', 2): 42000,
    ('bangalore', 'whitefield',   'apartment', 1): 17000,
    ('bangalore', 'whitefield',   'apartment', 2): 28000,
    ('bangalore', 'electronic city','apartment',1): 12000,
    ('bangalore', 'electronic city','apartment',2): 19000,
    ('bangalore', 'electronic city','pg',      1):  6500,
    ('bangalore', 'marathahalli', 'apartment', 1): 16000,
    ('bangalore', 'marathahalli', 'apartment', 2): 25000,
    ('bangalore', 'hsr layout',   'apartment', 1): 20000,
    ('bangalore', 'hsr layout',   'apartment', 2): 34000,
    ('bangalore', 'jp nagar',     'apartment', 1): 18000,
    ('bangalore', 'btm layout',   'apartment', 1): 16000,
    ('bangalore', 'btm layout',   'pg',        1):  7500,
    ('bangalore', 'jayanagar',    'apartment', 1): 19000,
    ('bangalore', 'malleshwaram', 'apartment', 1): 20000,
    ('bangalore', 'yelahanka',    'apartment', 1): 13000,
    ('bangalore', 'hebbal',       'apartment', 1): 18000,
    ('bangalore', 'sarjapur',     'apartment', 1): 15000,

    # ── Delhi ─────────────────────────────────────────────────────────────────
    ('delhi', 'lajpat nagar',    'apartment', 1): 18000,
    ('delhi', 'lajpat nagar',    'apartment', 2): 32000,
    ('delhi', 'south extension', 'apartment', 2): 42000,
    ('delhi', 'greater kailash', 'apartment', 2): 45000,
    ('delhi', 'hauz khas',       'apartment', 1): 22000,
    ('delhi', 'hauz khas',       'apartment', 2): 38000,
    ('delhi', 'dwarka',          'apartment', 1): 12000,
    ('delhi', 'dwarka',          'apartment', 2): 18000,
    ('delhi', 'rohini',          'apartment', 1): 10000,
    ('delhi', 'rohini',          'apartment', 2): 15000,
    ('delhi', 'janakpuri',       'apartment', 1): 12000,
    ('delhi', 'pitampura',       'apartment', 1): 11000,
    ('delhi', 'preet vihar',     'apartment', 1): 13000,
    ('delhi', 'vasant kunj',     'apartment', 2): 35000,
    ('delhi', 'saket',           'apartment', 2): 38000,
    ('delhi', 'nehru place',     'apartment', 1): 18000,
    ('delhi', 'karol bagh',      'apartment', 1): 15000,
    ('delhi', 'shahdara',        'apartment', 1):  9000,

    # ── Hyderabad ─────────────────────────────────────────────────────────────
    ('hyderabad', 'madhapur',    'apartment', 1): 15000,
    ('hyderabad', 'madhapur',    'apartment', 2): 25000,
    ('hyderabad', 'gachibowli',  'apartment', 1): 17000,
    ('hyderabad', 'gachibowli',  'apartment', 2): 28000,
    ('hyderabad', 'gachibowli',  'pg',        1):  7000,
    ('hyderabad', 'hitech city', 'apartment', 1): 18000,
    ('hyderabad', 'hitech city', 'apartment', 2): 30000,
    ('hyderabad', 'kondapur',    'apartment', 1): 14000,
    ('hyderabad', 'kondapur',    'apartment', 2): 22000,
    ('hyderabad', 'banjara hills','apartment', 1): 20000,
    ('hyderabad', 'banjara hills','apartment', 2): 35000,
    ('hyderabad', 'jubilee hills','apartment', 2): 38000,
    ('hyderabad', 'kukatpally',  'apartment', 1): 10000,
    ('hyderabad', 'kukatpally',  'apartment', 2): 15000,
    ('hyderabad', 'secunderabad','apartment', 1): 11000,
    ('hyderabad', 'begumpet',    'apartment', 1): 14000,
    ('hyderabad', 'dilsukhnagar','apartment', 1):  9000,
    ('hyderabad', 'miyapur',     'apartment', 1): 10000,

    # ── Chennai ───────────────────────────────────────────────────────────────
    ('chennai', 'anna nagar',    'apartment', 1): 16000,
    ('chennai', 'anna nagar',    'apartment', 2): 26000,
    ('chennai', 't nagar',       'apartment', 1): 17000,
    ('chennai', 't nagar',       'apartment', 2): 28000,
    ('chennai', 'velachery',     'apartment', 1): 12000,
    ('chennai', 'velachery',     'apartment', 2): 19000,
    ('chennai', 'adyar',         'apartment', 1): 18000,
    ('chennai', 'adyar',         'apartment', 2): 30000,
    ('chennai', 'omr',           'apartment', 1): 11000,
    ('chennai', 'omr',           'apartment', 2): 17000,
    ('chennai', 'porur',         'apartment', 1): 10000,
    ('chennai', 'perambur',      'apartment', 1):  9000,
    ('chennai', 'chromepet',     'apartment', 1):  9500,
    ('chennai', 'tambaram',      'apartment', 1):  8500,
    ('chennai', 'sholinganallur','apartment', 1): 12000,

    # ── Kolkata ───────────────────────────────────────────────────────────────
    ('kolkata', 'salt lake',     'apartment', 1): 12000,
    ('kolkata', 'salt lake',     'apartment', 2): 19000,
    ('kolkata', 'new town',      'apartment', 1): 10000,
    ('kolkata', 'new town',      'apartment', 2): 16000,
    ('kolkata', 'ballygunge',    'apartment', 1): 15000,
    ('kolkata', 'park street',   'apartment', 1): 18000,
    ('kolkata', 'alipore',       'apartment', 2): 25000,
    ('kolkata', 'behala',        'apartment', 1):  8000,
    ('kolkata', 'dum dum',       'apartment', 1):  8500,
    ('kolkata', 'howrah',        'apartment', 1):  7500,

    # ── Ahmedabad ─────────────────────────────────────────────────────────────
    ('ahmedabad', 'sg highway',  'apartment', 1): 11000,
    ('ahmedabad', 'sg highway',  'apartment', 2): 17000,
    ('ahmedabad', 'prahlad nagar','apartment', 1): 12000,
    ('ahmedabad', 'bodakdev',    'apartment', 1): 13000,
    ('ahmedabad', 'navrangpura', 'apartment', 1): 11000,
    ('ahmedabad', 'satellite',   'apartment', 1): 12000,
    ('ahmedabad', 'maninagar',   'apartment', 1):  8000,
    ('ahmedabad', 'vatva',       'apartment', 1):  7000,
    ('ahmedabad', 'bopal',       'apartment', 1): 10000,
    ('ahmedabad', 'thaltej',     'apartment', 1): 11500,

    # ══════════════════════════════════════════════════════════════
    # COMMERCIAL — SHOPS
    # ══════════════════════════════════════════════
    ('mumbai',     'bandra',         'shop', 1): 80000,
    ('mumbai',     'borivali',       'shop', 1): 30000,
    ('mumbai',     'lower parel',    'shop', 1): 90000,
    ('mumbai',     'dadar',          'shop', 1): 50000,
    ('pune',       'koregaon park',  'shop', 1): 35000,
    ('pune',       'wakad',          'shop', 1): 22000,
    ('pune',       'baner',          'shop', 1): 25000,
    ('bangalore',  'koramangala',    'shop', 1): 60000,
    ('bangalore',  'indiranagar',    'shop', 1): 70000,
    ('bangalore',  'marathahalli',   'shop', 1): 35000,
    ('delhi',      'lajpat nagar',   'shop', 1): 55000,
    ('delhi',      'hauz khas',      'shop', 1): 65000,
    ('delhi',      'karol bagh',     'shop', 1): 45000,
    ('hyderabad',  'banjara hills',  'shop', 1): 45000,
    ('hyderabad',  'madhapur',       'shop', 1): 30000,
    ('chennai',    't nagar',        'shop', 1): 40000,
    ('chennai',    'anna nagar',     'shop', 1): 35000,

    # ══════════════════════════════════════════════════════════════
    # COMMERCIAL — OFFICES
    # ══════════════════════════════════════════════════════════════
    ('mumbai',     'andheri',        'office', 1): 35000,
    ('mumbai',     'bandra',         'office', 1): 55000,
    ('mumbai',     'lower parel',    'office', 1): 90000,
    ('mumbai',     'powai',          'office', 1): 40000,
    ('pune',       'hinjewadi',      'office', 1): 20000,
    ('pune',       'koregaon park',  'office', 1): 25000,
    ('pune',       'baner',          'office', 1): 22000,
    ('bangalore',  'koramangala',    'office', 1): 45000,
    ('bangalore',  'whitefield',     'office', 1): 30000,
    ('bangalore',  'indiranagar',    'office', 1): 50000,
    ('bangalore',  'electronic city','office', 1): 22000,
    ('delhi',      'nehru place',    'office', 1): 45000,
    ('delhi',      'hauz khas',      'office', 1): 40000,
    ('delhi',      'dwarka',         'office', 1): 22000,
    ('hyderabad',  'hitech city',    'office', 1): 35000,
    ('hyderabad',  'madhapur',       'office', 1): 28000,
    ('chennai',    'omr',            'office', 1): 20000,
    ('chennai',    'anna nagar',     'office', 1): 25000,

    # ══════════════════════════════════════════════════════════════
    # COMMERCIAL — WAREHOUSES
    # ══════════════════════════════════════════════════════════════
    ('mumbai',     'andheri',        'warehouse', 1): 25000,
    ('mumbai',     'navi mumbai',    'warehouse', 1): 18000,
    ('pune',       'hadapsar',       'warehouse', 1): 15000,
    ('pune',       'pimpri',         'warehouse', 1): 12000,
    ('bangalore',  'electronic city','warehouse', 1): 18000,
    ('bangalore',  'whitefield',     'warehouse', 1): 20000,
    ('hyderabad',  'kukatpally',     'warehouse', 1): 15000,
    ('delhi',      'dwarka',         'warehouse', 1): 20000,
    ('chennai',    'tambaram',       'warehouse', 1): 12000,

    # ══════════════════════════════════════════════════════════════
    # COMMERCIAL — SHOWROOMS
    # ══════════════════════════════════════════════════════════════
    ('mumbai',     'andheri',        'showroom', 1): 70000,
    ('mumbai',     'bandra',         'showroom', 1): 120000,
    ('bangalore',  'marathahalli',   'showroom', 1): 55000,
    ('delhi',      'nehru place',    'showroom', 1): 70000,
    ('hyderabad',  'banjara hills',  'showroom', 1): 60000,
    ('pune',       'viman nagar',    'showroom', 1): 40000,

    # ══════════════════════════════════════════════════════════════
    # COMMERCIAL — COWORKING (per seat/month)
    # ══════════════════════════════════════════════════════════════
    ('mumbai',     'lower parel',    'coworking', 1): 8000,
    ('mumbai',     'andheri',        'coworking', 1): 6000,
    ('pune',       'hinjewadi',      'coworking', 1): 4500,
    ('pune',       'koregaon park',  'coworking', 1): 5500,
    ('bangalore',  'koramangala',    'coworking', 1): 6000,
    ('bangalore',  'indiranagar',    'coworking', 1): 7000,
    ('hyderabad',  'hitech city',    'coworking', 1): 5000,
    ('delhi',      'hauz khas',      'coworking', 1): 6500,
    ('chennai',    'omr',            'coworking', 1): 4000,

    # ══════════════════════════════════════════════════════════════
    # SPECIAL PROPERTIES
    # ══════════════════════════════════════════════════════════════
    ('mumbai',     'andheri',        'studio_space', 1): 30000,
    ('bangalore',  'koramangala',    'studio_space', 1): 20000,
    ('delhi',      'hauz khas',      'studio_space', 1): 25000,
    ('pune',       'koregaon park',  'studio_space', 1): 15000,
    ('mumbai',     'borivali',       'event_hall',   1): 50000,
    ('pune',       'koregaon park',  'event_hall',   1): 35000,
    ('bangalore',  'koramangala',    'event_hall',   1): 40000,
    ('mumbai',     'andheri',        'garage',       1): 5000,
    ('bangalore',  'koramangala',    'garage',       1): 3500,
    ('pune',       'wakad',          'garage',       1): 2500,
    ('delhi',      'dwarka',         'garage',       1): 3000,
    ('pune',       'wakad',          'farmhouse',    1): 25000,
    ('mumbai',     'karjat',         'farmhouse',    1): 40000,
    ('bangalore',  'whitefield',     'farmhouse',    1): 30000,
}


# ══════════════════════════════════════════════════════════════════════════════
# MARKET RENT LOOKUP
# ══════════════════════════════════════════════════════════════════════════════

def get_market_rent(
    city:         str,
    locality:     str,
    listing_type: str,
    bedrooms:     int,
) -> Optional[int]:
    """
    Retrieve the market average rent for a location.

    Lookup order (most specific → least specific):
      1. Exact (city, locality, type, bedrooms)
      2. Same city + type + bedrooms (different locality)
      3. Same city + bedrooms only
      4. None (insufficient data)

    Args:
        city, locality, listing_type, bedrooms: location parameters.

    Returns:
        Average rent in ₹ or None if no data available.
    """
    city    = city.lower().strip()
    locality = locality.lower().strip()
    ltype   = listing_type.lower().strip()

    # ── 1. Exact match ─────────────────────────────────────────────────────────
    key = (city, locality, ltype, bedrooms)
    if key in SEED_MARKET_DATA:
        return SEED_MARKET_DATA[key]

    # ── 2. Same city + type + bedrooms (average across localities) ─────────────
    city_type_bed = [
        v for (c, l, t, b), v in SEED_MARKET_DATA.items()
        if c == city and t == ltype and b == bedrooms
    ]
    if city_type_bed:
        return round(sum(city_type_bed) / len(city_type_bed))

    # ── 3. Same city + bedrooms only ───────────────────────────────────────────
    city_bed = [
        v for (c, l, t, b), v in SEED_MARKET_DATA.items()
        if c == city and b == bedrooms
    ]
    if city_bed:
        return round(sum(city_bed) / len(city_bed))

    # ── 4. Same city any bedroom → scale ──────────────────────────────────────
    city_any = [
        v for (c, l, t, b), v in SEED_MARKET_DATA.items()
        if c == city and t == ltype
    ]
    if city_any:
        avg_1bhk = round(sum(city_any) / len(city_any))
        # Scale by bedroom count: 1BHK=1x, 2BHK=1.6x, 3BHK=2.2x
        scale = {1: 1.0, 2: 1.6, 3: 2.2, 4: 2.8}.get(bedrooms, 1.0)
        return round(avg_1bhk * scale)

    return None


# ══════════════════════════════════════════════════════════════════════════════
# PRICE ESTIMATOR (Feature 3)
# ══════════════════════════════════════════════════════════════════════════════

def estimate_price(listing: dict) -> Dict:
    """
    Analyse a listing's rent vs market rate.

    Args:
        listing: dict with keys:
          city, locality, listing_type, bedrooms, rent

    Returns:
        {
            'market_rent':    20000,
            'listed_rent':    25000,
            'difference_pct': 25.0,       # + means overpriced
            'verdict':        'overpriced',
            'label':          '25% overpriced',
            'explanation':    'Market rent in Andheri for 1BHK...',
            'confidence':     'high' | 'medium' | 'low',
            'price_range': {
                'low':  18000,
                'fair': 20000,
                'high': 23000,
            }
        }
    """
    city        = listing.get('city',         '').strip()
    locality    = listing.get('locality',     '').strip()
    ltype       = listing.get('listing_type', 'apartment').strip()
    bedrooms    = int(listing.get('bedrooms', 1))
    rent        = int(listing.get('rent',     0))

    market_rent = get_market_rent(city, locality, ltype, bedrooms)

    # ── No data available ──────────────────────────────────────────────────────
    if not market_rent:
        return {
            'market_rent':    None,
            'listed_rent':    rent,
            'difference_pct': None,
            'verdict':        'unknown',
            'label':          'Insufficient market data',
            'explanation':    (
                f'Not enough market data for {ltype}s in '
                f'{locality.title() or city.title()} '
                f'to evaluate this price.'
            ),
            'confidence':  'low',
            'price_range': None,
        }

    # ── Compute difference ─────────────────────────────────────────────────────
    diff_pct = round(((rent - market_rent) / market_rent) * 100, 1)

    # ── Verdict ────────────────────────────────────────────────────────────────
    if diff_pct > 25:
        verdict = 'overpriced'
        label   = f'{abs(diff_pct):.0f}% overpriced'
    elif diff_pct > 10:
        verdict = 'overpriced'
        label   = f'{abs(diff_pct):.0f}% above market'
    elif diff_pct < -25:
        verdict = 'underpriced'
        label   = f'{abs(diff_pct):.0f}% below market — verify carefully'
    elif diff_pct < -10:
        verdict = 'underpriced'
        label   = f'{abs(diff_pct):.0f}% below market'
    else:
        verdict = 'fair'
        label   = 'Fair market price'

    # ── Explanation ────────────────────────────────────────────────────────────
    loc_display = (
        f'{locality.title()}, {city.title()}' if locality
        else city.title()
    )
    bed_label = (
        f'{bedrooms}BHK'
        if ltype not in ('pg', 'shared_room', 'studio')
        else ltype.replace('_', ' ').title()
    )

    if verdict == 'fair':
        explanation = (
            f'Market rent for a {bed_label} {ltype} in {loc_display} '
            f'is approximately ₹{market_rent:,}/mo. '
            f'This listing is priced fairly.'
        )
    elif verdict == 'overpriced':
        explanation = (
            f'Market rent for a {bed_label} {ltype} in {loc_display} '
            f'is approximately ₹{market_rent:,}/mo. '
            f'This listing at ₹{rent:,}/mo is {label}. '
            f'You may be able to negotiate down.'
        )
    else:
        explanation = (
            f'Market rent for a {bed_label} {ltype} in {loc_display} '
            f'is approximately ₹{market_rent:,}/mo. '
            f'This listing at ₹{rent:,}/mo is {label}. '
            f'Verify this is not a fraudulent listing.'
        )

    # ── Confidence based on lookup specificity ─────────────────────────────────
    exact_key = (
        city.lower(), locality.lower(),
        ltype.lower(), bedrooms
    )
    if exact_key in SEED_MARKET_DATA:
        confidence = 'high'
    elif any(
        c == city.lower() and t == ltype.lower() and b == bedrooms
        for c, l, t, b in SEED_MARKET_DATA
    ):
        confidence = 'medium'
    else:
        confidence = 'low'

    # ── Price range bands ──────────────────────────────────────────────────────
    price_range = {
        'low':  round(market_rent * 0.80),
        'fair': market_rent,
        'high': round(market_rent * 1.25),
    }

    return {
        'market_rent':    market_rent,
        'listed_rent':    rent,
        'difference_pct': diff_pct,
        'verdict':        verdict,
        'label':          label,
        'explanation':    explanation,
        'confidence':     confidence,
        'price_range':    price_range,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCAM DETECTION ENGINE (Feature 7)
# ══════════════════════════════════════════════════════════════════════════════

# Each rule: { id, description, weight, check_fn }
# weight = how many risk points this rule adds when triggered

SCAM_RULES = [
    {
        'id':          'price_too_low',
        'description': 'Rent is 40%+ below market price',
        'weight':      40,
    },
    {
        'id':          'price_extremely_low',
        'description': 'Rent is 60%+ below market price (extremely suspicious)',
        'weight':      20,   # Extra 20 on top of price_too_low
    },
    {
        'id':          'unverified_owner',
        'description': 'Owner has not completed identity verification',
        'weight':      25,
    },
    {
        'id':          'no_photos',
        'description': 'No photos uploaded for this listing',
        'weight':      18,
    },
    {
        'id':          'very_few_photos',
        'description': 'Only 1 photo uploaded (insufficient for verification)',
        'weight':      8,
    },
    {
        'id':          'no_utility_bill',
        'description': 'No utility bill uploaded as ownership proof',
        'weight':      12,
    },
    {
        'id':          'new_account',
        'description': 'Owner account created less than 7 days ago',
        'weight':      10,
    },
    {
        'id':          'very_new_account',
        'description': 'Owner account created less than 24 hours ago',
        'weight':      10,   # Extra 10 on top of new_account
    },
]

# Total possible risk score:
# price_too_low + price_extremely_low + unverified_owner + no_photos
# + no_utility_bill + new_account + very_new_account = 135
# We cap at 100 when reporting.

SCAM_FLAG_THRESHOLD = 50   # >= 50 risk points = flagged
CAUTION_THRESHOLD   = 30   # >= 30 = caution


def detect_scam(
    listing:        dict,
    owner:          dict,
    price_analysis: dict,
) -> Dict:
    """
    Run all scam detection rules against a listing.

    Args:
        listing: dict with:
          photos          → list of photo URLs
          trust_info      → dict with bill_uploaded (bool)

        owner: dict with:
          id_verified     → bool
          account_age_days → int

        price_analysis: output of estimate_price()

    Returns:
        {
            'is_scam':    True,
            'risk_score': 75,
            'reasons': [
                'Rent is 55% below market price',
                'Owner has not verified their identity',
            ],
            'badge': '⚠️ Suspicious Listing',
            'badge_class': 'scam',
            'rules_triggered': ['price_too_low', 'unverified_owner'],
        }
    """
    risk_score      = 0
    reasons         = []
    rules_triggered = []

    photos       = listing.get('photos', []) or []
    trust_info   = listing.get('trust_info', {}) or {}
    bill_uploaded = trust_info.get('bill_uploaded', False)
    id_verified   = owner.get('id_verified', False)
    account_age   = owner.get('account_age_days', 365)
    diff_pct      = price_analysis.get('difference_pct')

    # ── Rule 1: Price too low ──────────────────────────────────────────────────
    if diff_pct is not None and diff_pct < -40:
        risk_score += 40
        reasons.append(
            f'Rent is {abs(diff_pct):.0f}% below market price'
        )
        rules_triggered.append('price_too_low')

        # ── Rule 1b: Extremely low ─────────────────────────────────────────────
        if diff_pct < -60:
            risk_score += 20
            reasons.append(
                'Rent is extremely below market — high fraud risk'
            )
            rules_triggered.append('price_extremely_low')

    # ── Rule 2: Unverified owner ───────────────────────────────────────────────
    if not id_verified:
        risk_score += 25
        reasons.append(
            'Owner has not verified their identity'
        )
        rules_triggered.append('unverified_owner')

    # ── Rule 3a: No photos ─────────────────────────────────────────────────────
    if len(photos) == 0:
        risk_score += 18
        reasons.append(
            'No photos uploaded — cannot verify property exists'
        )
        rules_triggered.append('no_photos')

    # ── Rule 3b: Very few photos ───────────────────────────────────────────────
    elif len(photos) == 1:
        risk_score += 8
        reasons.append(
            'Only 1 photo uploaded — insufficient visual verification'
        )
        rules_triggered.append('very_few_photos')

    # ── Rule 4: No utility bill ────────────────────────────────────────────────
    if not bill_uploaded:
        risk_score += 12
        reasons.append(
            'No utility bill uploaded to prove property ownership'
        )
        rules_triggered.append('no_utility_bill')

    # ── Rule 5a: New account ───────────────────────────────────────────────────
    if account_age < 7:
        risk_score += 10
        reasons.append(
            f'Owner account created only {account_age} day(s) ago'
        )
        rules_triggered.append('new_account')

        # ── Rule 5b: Very new account ──────────────────────────────────────────
        if account_age < 1:
            risk_score += 10
            reasons.append(
                'Owner account created within the last 24 hours'
            )
            rules_triggered.append('very_new_account')

    # ── Cap risk score at 100 ──────────────────────────────────────────────────
    risk_score = min(100, risk_score)

    # ── Determine badge ────────────────────────────────────────────────────────
    is_scam    = risk_score >= SCAM_FLAG_THRESHOLD
    is_caution = risk_score >= CAUTION_THRESHOLD

    if is_scam:
        badge       = '⚠️ Suspicious Listing — Verify Before Proceeding'
        badge_class = 'scam'
    elif is_caution:
        badge       = '⚡ Exercise Caution'
        badge_class = 'caution'
    else:
        badge       = '✅ Looks Legitimate'
        badge_class = 'safe'

    return {
        'is_scam':         is_scam,
        'is_caution':      is_caution,
        'risk_score':      risk_score,
        'reasons':         reasons,
        'badge':           badge,
        'badge_class':     badge_class,
        'rules_triggered': rules_triggered,
    }


# ══════════════════════════════════════════════════════════════════════════════
# BULK PRICE CHECK (for admin dashboard / analytics)
# ══════════════════════════════════════════════════════════════════════════════

def bulk_price_check(listings: List[dict]) -> List[dict]:
    """
    Run price estimation on a list of listing dicts.
    Returns each listing enriched with price analysis.

    Args:
        listings: List of listing dicts (each with city, locality,
                  listing_type, bedrooms, rent).

    Returns:
        List of dicts: { ...listing, 'price_analysis': {...} }
    """
    results = []
    for listing in listings:
        analysis = estimate_price(listing)
        results.append({
            **listing,
            'price_analysis': analysis,
        })
    return results


# ══════════════════════════════════════════════════════════════════════════════
# MARKET SUMMARY (for analytics dashboard)
# ══════════════════════════════════════════════════════════════════════════════

def get_market_summary(city: str) -> Dict:
    """
    Return a summary of market rents for a city.
    Used by analytics/market_price dashboard.

    Args:
        city: City name (case-insensitive).

    Returns:
        {
            'city': 'Mumbai',
            'localities': {
                'Andheri': {'1bhk': 25000, '2bhk': 42000, 'pg': 9000},
                ...
            },
            'avg_1bhk': 22000,
            'avg_2bhk': 36000,
        }
    """
    city_lower  = city.lower().strip()
    localities  = {}

    for (c, loc, ltype, beds), rent in SEED_MARKET_DATA.items():
        if c != city_lower:
            continue
        loc_title = loc.title()
        if loc_title not in localities:
            localities[loc_title] = {}
        key = f'{beds}bhk' if ltype == 'apartment' else ltype
        localities[loc_title][key] = rent

    # City-wide averages
    all_1bhk = [
        v for (c, l, t, b), v in SEED_MARKET_DATA.items()
        if c == city_lower and t == 'apartment' and b == 1
    ]
    all_2bhk = [
        v for (c, l, t, b), v in SEED_MARKET_DATA.items()
        if c == city_lower and t == 'apartment' and b == 2
    ]

    return {
        'city':       city.title(),
        'localities': localities,
        'avg_1bhk':   round(sum(all_1bhk) / len(all_1bhk)) if all_1bhk else 0,
        'avg_2bhk':   round(sum(all_2bhk) / len(all_2bhk)) if all_2bhk else 0,
    }