"""
NestMate — Agreements Views
Feature 9: Instant Rental Agreement PDF Generator + E-Signature

Django Views handle:
  - Agreement creation form
  - PDF generation via ReportLab
  - Agreement detail / preview page
  - E-signature (tenant + owner sign)
  - Download PDF
  - List all agreements for current user
  - Agreement status tracking (draft → pending → active → expired)
"""

"""
NestMate — Agreements Views
Feature 9: Instant Rental Agreement PDF Generator + E-Signature
"""

import os
from datetime import datetime, date

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import FileResponse, JsonResponse, HttpResponse
from django.views import View
from django.conf import settings

from apps.listings.models import RentalAgreement, Listing, ChatRoom
from apps.accounts.models import User
from ml.agreement_generator import generate_agreement_pdf


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_mongo_user(django_user):
    return User.objects(email=django_user.email).first()


def _get_pdf_path(agreement_id: str) -> str:
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'agreements')
    os.makedirs(pdf_dir, exist_ok=True)
    return os.path.join(pdf_dir, f'agreement_{agreement_id}.pdf')


def _get_pdf_url(agreement_id: str) -> str:
    return f'/media/agreements/agreement_{agreement_id}.pdf'


def _check_access(agreement: RentalAgreement, mongo_user: User) -> bool:
    return (
        str(agreement.tenant.id) == str(mongo_user.id) or
        str(agreement.owner.id)  == str(mongo_user.id)
    )


def _build_agreement_data(agreement: RentalAgreement, tenant_address='', owner_address='') -> dict:
    return {
        'tenant_name':    agreement.tenant.full_name or agreement.tenant.username,
        'tenant_phone':   agreement.tenant.phone or '',
        'tenant_address': tenant_address or agreement.tenant_address or '',
        'owner_name':     agreement.owner.full_name or agreement.owner.username,
        'owner_phone':    agreement.owner.phone or '',
        'owner_address':  owner_address or agreement.owner_address or '',
        'property_address': (
            agreement.listing.location.address
            if agreement.listing and agreement.listing.location
            else ''
        ),
        'rent':            agreement.rent,
        'deposit':         agreement.deposit,
        'maintenance':     agreement.maintenance,
        'duration_months': agreement.duration_months,
        'start_date':      agreement.start_date.strftime('%d %B %Y') if agreement.start_date else '',
        'end_date':        agreement.end_date.strftime('%d %B %Y')   if agreement.end_date   else '',
        'custom_terms':    agreement.custom_terms or [],
    }


# ══════════════════════════════════════════════════════════════════════════════
# 1. LIST ALL AGREEMENTS
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class AgreementListView(View):
    def get(self, request):
        mongo_user = get_mongo_user(request.user)

        as_tenant = list(RentalAgreement.objects(tenant=mongo_user).order_by('-created_at'))
        as_owner  = list(RentalAgreement.objects(owner=mongo_user).order_by('-created_at'))

        seen_ids = set()
        all_agreements = []
        for a in as_tenant + as_owner:
            aid = str(a.id)
            if aid not in seen_ids:
                seen_ids.add(aid)
                all_agreements.append(a)

        all_agreements.sort(key=lambda a: a.created_at or datetime.min, reverse=True)

        # Return JSON for React
        if request.headers.get('Accept') == 'application/json':
            data = []
            for a in all_agreements:
                data.append({
                    'id':             str(a.id),
                    'listing_title':  a.listing.title if a.listing else '',
                    'listing_id':     str(a.listing.id) if a.listing else '',
                    'tenant_name':    a.tenant.full_name or a.tenant.username if a.tenant else '',
                    'owner_name':     a.owner.full_name  or a.owner.username  if a.owner  else '',
                    'rent':           a.rent,
                    'deposit':        a.deposit or 0,
                    'duration_months': a.duration_months,
                    'start_date':     a.start_date.strftime('%d %b %Y') if a.start_date else '',
                    'end_date':       a.end_date.strftime('%d %b %Y')   if a.end_date   else '',
                    'status':         a.status,
                    'tenant_signed':  a.tenant_signed,
                    'owner_signed':   a.owner_signed,
                    'pdf_url':        a.pdf_url or '',
                })
            return JsonResponse({'agreements': data})

        # Build data for ALL requests (not just JSON Accept header)
        data = []
        for a in all_agreements:
            data.append({
                'id':              str(a.id),
                'listing_title':   a.listing.title if a.listing else '',
                'listing_id':      str(a.listing.id) if a.listing else '',
                'tenant_name':     a.tenant.full_name or a.tenant.username if a.tenant else '',
                'owner_name':      a.owner.full_name  or a.owner.username  if a.owner  else '',
                'rent':            a.rent,
                'deposit':         a.deposit or 0,
                'duration_months': a.duration_months,
                'start_date':      a.start_date.strftime('%d %b %Y') if a.start_date else '',
                'end_date':        a.end_date.strftime('%d %b %Y')   if a.end_date   else '',
                'status':          a.status,
                'tenant_signed':   a.tenant_signed,
                'owner_signed':    a.owner_signed,
                'pdf_url':         a.pdf_url or '',
            })
        return JsonResponse({'agreements': data})

# ══════════════════════════════════════════════════════════════════════════════
# 2. CREATE AGREEMENT
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class CreateAgreementView(View):
    def get(self, request, listing_id):
        try:
            listing = Listing.objects.get(id=listing_id)
        except Exception:
            return JsonResponse({'error': 'Listing not found'}, status=404)

        mongo_user  = get_mongo_user(request.user)
        agreed_rent = listing.rent

        chat_room = ChatRoom.objects(listing=listing, status='deal_done').first()
        if chat_room and chat_room.agreed_rent:
            agreed_rent = chat_room.agreed_rent

        today     = date.today()
        end_month = today.month + 11
        end_year  = today.year + (end_month - 1) // 12
        end_month = ((end_month - 1) % 12) + 1
        end_date  = date(end_year, end_month, today.day)

        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'listing_id':   str(listing.id),
                'listing_title': listing.title,
                'rent':         agreed_rent,
                'deposit':      listing.deposit or 0,
                'start_date':   today.strftime('%Y-%m-%d'),
                'end_date':     end_date.strftime('%Y-%m-%d'),
            })

        return render(request, 'agreements/create.html', {'listing': listing})

    def post(self, request, listing_id):
        mongo_user = get_mongo_user(request.user)

        try:
            listing = Listing.objects.get(id=listing_id)
        except Exception:
            return JsonResponse({'error': 'Listing not found'}, status=404)

        # Parse body — support both JSON and form data
        try:
            import json
            data = json.loads(request.body)
        except Exception:
            data = request.POST.dict()

        # Dates
        try:
            start_date = datetime.strptime(data.get('start_date', ''), '%Y-%m-%d')
            end_date   = datetime.strptime(data.get('end_date',   ''), '%Y-%m-%d')
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        if end_date <= start_date:
            return JsonResponse({'error': 'End date must be after start date.'}, status=400)

        delta_days      = (end_date - start_date).days
        duration_months = max(1, round(delta_days / 30))

        # Financials
        try:
            rent        = int(data.get('rent',        listing.rent))
            deposit     = int(data.get('deposit',     listing.deposit or 0))
            maintenance = int(data.get('maintenance', 0))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid financial values.'}, status=400)

        if rent <= 0:
            return JsonResponse({'error': 'Rent must be greater than zero.'}, status=400)

        # Custom terms
        custom_terms_raw = data.get('custom_terms', '')
        if isinstance(custom_terms_raw, list):
            custom_terms = custom_terms_raw
        else:
            custom_terms = [t.strip() for t in custom_terms_raw.split('\n') if t.strip()]

        tenant_address = data.get('tenant_address', '').strip()
        owner_address  = data.get('owner_address',  '').strip()

        is_owner = str(listing.owner.id) == str(mongo_user.id)

        if is_owner:
            tenant_id   = data.get('tenant_id', '')
            tenant_user = User.objects(id=tenant_id).first() if tenant_id else None
            if not tenant_user:
                return JsonResponse({'error': 'Please specify the tenant.'}, status=400)
            owner_user = mongo_user
        else:
            tenant_user = mongo_user
            owner_user  = listing.owner

        # Create agreement
        agreement = RentalAgreement(
            listing         = listing,
            tenant          = tenant_user,
            owner           = owner_user,
            rent            = rent,
            deposit         = deposit,
            maintenance     = maintenance,
            duration_months = duration_months,
            start_date      = start_date,
            end_date        = end_date,
            tenant_address  = tenant_address,
            owner_address   = owner_address,
            custom_terms    = custom_terms,
            status          = 'draft',
        )
        agreement.save()

        # Generate PDF
        pdf_path = _get_pdf_path(str(agreement.id))
        pdf_url  = _get_pdf_url(str(agreement.id))

        try:
            agreement_data = _build_agreement_data(agreement, tenant_address, owner_address)
            generate_agreement_pdf(agreement_data, pdf_path)
            agreement.update(pdf_url=pdf_url, status='pending')
        except Exception as e:
            return JsonResponse({
                'id':      str(agreement.id),
                'warning': f'Agreement saved but PDF failed: {str(e)}',
            }, status=201)

        return JsonResponse({
            'id':      str(agreement.id),
            'pdf_url': pdf_url,
            'message': 'Agreement created and PDF generated.',
        }, status=201)


# ══════════════════════════════════════════════════════════════════════════════
# 3. AGREEMENT DETAIL
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class AgreementDetailView(View):
    def get(self, request, agreement_id):
        mongo_user = get_mongo_user(request.user)

        try:
            agreement = RentalAgreement.objects.get(id=agreement_id)
        except Exception:
            return JsonResponse({'error': 'Agreement not found'}, status=404)

        if not _check_access(agreement, mongo_user):
            return JsonResponse({'error': 'Access denied'}, status=403)

        is_tenant  = str(agreement.tenant.id) == str(mongo_user.id)
        is_owner   = str(agreement.owner.id)  == str(mongo_user.id)
        pdf_exists = os.path.exists(_get_pdf_path(agreement_id))

        data = {
            'id':             str(agreement.id),
            'listing_id':     str(agreement.listing.id) if agreement.listing else '',
            'listing_title':  agreement.listing.title   if agreement.listing else '',
            'tenant_name':    agreement.tenant.full_name or agreement.tenant.username,
            'tenant_phone':   agreement.tenant.phone or '',
            'tenant_address': agreement.tenant_address or '',
            'owner_name':     agreement.owner.full_name or agreement.owner.username,
            'owner_phone':    agreement.owner.phone or '',
            'owner_address':  agreement.owner_address or '',
            'rent':           agreement.rent,
            'deposit':        agreement.deposit or 0,
            'maintenance':    agreement.maintenance or 0,
            'duration_months': agreement.duration_months,
            'start_date':     agreement.start_date.strftime('%d %B %Y') if agreement.start_date else '',
            'end_date':       agreement.end_date.strftime('%d %B %Y')   if agreement.end_date   else '',
            'custom_terms':   agreement.custom_terms or [],
            'status':         agreement.status,
            'tenant_signed':  agreement.tenant_signed,
            'owner_signed':   agreement.owner_signed,
            'tenant_signed_at': agreement.tenant_signed_at.strftime('%d %b %Y') if agreement.tenant_signed_at else '',
            'owner_signed_at':  agreement.owner_signed_at.strftime('%d %b %Y')  if agreement.owner_signed_at  else '',
            'pdf_url':        agreement.pdf_url or '',
            'pdf_exists':     pdf_exists,
            'is_tenant':      is_tenant,
            'is_owner':       is_owner,
            'both_signed':    agreement.both_signed(),
            'can_sign_as_tenant': (is_tenant and not agreement.tenant_signed and agreement.status in ('pending','draft')),
            'can_sign_as_owner':  (is_owner  and not agreement.owner_signed  and agreement.status in ('pending','draft')),
        }

        if request.headers.get('Accept') == 'application/json':
            return JsonResponse(data)

        return JsonResponse(data)

# ══════════════════════════════════════════════════════════════════════════════
# 4. DOWNLOAD PDF
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class DownloadAgreementView(View):
    def get(self, request, agreement_id):
        mongo_user = get_mongo_user(request.user)

        try:
            agreement = RentalAgreement.objects.get(id=agreement_id)
        except Exception:
            return JsonResponse({'error': 'Agreement not found'}, status=404)

        if not _check_access(agreement, mongo_user):
            return JsonResponse({'error': 'Access denied'}, status=403)

        pdf_path = _get_pdf_path(agreement_id)

        if not os.path.exists(pdf_path):
            try:
                agreement_data = _build_agreement_data(agreement)
                generate_agreement_pdf(agreement_data, pdf_path)
                agreement.update(pdf_url=_get_pdf_url(agreement_id))
            except Exception as e:
                return JsonResponse({'error': f'PDF generation failed: {str(e)}'}, status=500)

        filename = f'NestMate_Agreement_{agreement_id[:8]}.pdf'
        response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ══════════════════════════════════════════════════════════════════════════════
# 5. VIEW PDF IN BROWSER
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class ViewAgreementPDFView(View):
    def get(self, request, agreement_id):
        mongo_user = get_mongo_user(request.user)

        try:
            agreement = RentalAgreement.objects.get(id=agreement_id)
        except Exception:
            return HttpResponse('Agreement not found', status=404)

        if not _check_access(agreement, mongo_user):
            return HttpResponse('Access denied', status=403)

        pdf_path = _get_pdf_path(agreement_id)

        if not os.path.exists(pdf_path):
            try:
                agreement_data = _build_agreement_data(agreement)
                generate_agreement_pdf(agreement_data, pdf_path)
            except Exception as e:
                return HttpResponse(f'PDF generation failed: {str(e)}', status=500)

        response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="agreement_{agreement_id}.pdf"'
        return response


# ══════════════════════════════════════════════════════════════════════════════
# 6. E-SIGN
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class SignAgreementView(View):
    def post(self, request, agreement_id):
        mongo_user = get_mongo_user(request.user)

        try:
            import json
            body = json.loads(request.body)
            role = body.get('role', '')
        except Exception:
            role = request.POST.get('role', '')

        try:
            agreement = RentalAgreement.objects.get(id=agreement_id)
        except Exception:
            return JsonResponse({'error': 'Agreement not found'}, status=404)

        if not _check_access(agreement, mongo_user):
            return JsonResponse({'error': 'Access denied'}, status=403)

        if agreement.status == 'expired':
            return JsonResponse({'error': 'Agreement has expired.'}, status=400)

        now = datetime.utcnow()

        if role == 'tenant':
            if str(agreement.tenant.id) != str(mongo_user.id):
                return JsonResponse({'error': 'Only tenant can sign as tenant.'}, status=403)
            if agreement.tenant_signed:
                return JsonResponse({'error': 'Already signed.'}, status=400)
            agreement.update(tenant_signed=True, tenant_signed_at=now)

        elif role == 'owner':
            if str(agreement.owner.id) != str(mongo_user.id):
                return JsonResponse({'error': 'Only owner can sign as owner.'}, status=403)
            if agreement.owner_signed:
                return JsonResponse({'error': 'Already signed.'}, status=400)
            agreement.update(owner_signed=True, owner_signed_at=now)

        else:
            return JsonResponse({'error': 'Invalid role.'}, status=400)

        # Check if both signed
        refreshed = RentalAgreement.objects.get(id=agreement_id)

        if refreshed.tenant_signed and refreshed.owner_signed:
            refreshed.update(status='active', updated_at=now)
            # Regenerate PDF with signature dates
            try:
                pdf_path       = _get_pdf_path(agreement_id)
                agreement_data = _build_agreement_data(refreshed)
                agreement_data['tenant_signed_at'] = refreshed.tenant_signed_at.strftime('%d %B %Y') if refreshed.tenant_signed_at else ''
                agreement_data['owner_signed_at']  = refreshed.owner_signed_at.strftime('%d %B %Y')  if refreshed.owner_signed_at  else ''
                generate_agreement_pdf(agreement_data, pdf_path)
            except Exception:
                pass

            return JsonResponse({
                'message':    'Agreement is now ACTIVE! Both parties have signed.',
                'status':     'active',
                'both_signed': True,
            })

        return JsonResponse({
            'message':    f'{role.title()} signature recorded.',
            'status':     refreshed.status,
            'both_signed': False,
        })


# ══════════════════════════════════════════════════════════════════════════════
# 7. REGENERATE PDF
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class RegeneratePDFView(View):
    def post(self, request, agreement_id):
        mongo_user = get_mongo_user(request.user)

        try:
            agreement = RentalAgreement.objects.get(id=agreement_id)
        except Exception:
            return JsonResponse({'error': 'Agreement not found'}, status=404)

        if not _check_access(agreement, mongo_user):
            return JsonResponse({'error': 'Access denied'}, status=403)

        try:
            pdf_path       = _get_pdf_path(agreement_id)
            agreement_data = _build_agreement_data(agreement)
            generate_agreement_pdf(agreement_data, pdf_path)
            agreement.update(pdf_url=_get_pdf_url(agreement_id))
            return JsonResponse({'message': 'PDF regenerated.', 'pdf_url': _get_pdf_url(agreement_id)})
        except Exception as e:
            return JsonResponse({'error': f'PDF generation failed: {str(e)}'}, status=500)


# ══════════════════════════════════════════════════════════════════════════════
# 8. DELETE AGREEMENT
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class DeleteAgreementView(View):
    def post(self, request, agreement_id):
        mongo_user = get_mongo_user(request.user)

        try:
            agreement = RentalAgreement.objects.get(id=agreement_id)
        except Exception:
            return JsonResponse({'error': 'Agreement not found'}, status=404)

        if not _check_access(agreement, mongo_user):
            return JsonResponse({'error': 'Access denied'}, status=403)

        if agreement.status not in ('draft',):
            return JsonResponse({'error': 'Only draft agreements can be deleted.'}, status=400)

        pdf_path = _get_pdf_path(agreement_id)
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except OSError:
                pass

        agreement.delete()
        return JsonResponse({'message': 'Agreement deleted.'})


# ══════════════════════════════════════════════════════════════════════════════
# 9. STATUS API
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def agreement_status_api(request, agreement_id):
    mongo_user = get_mongo_user(request.user)

    try:
        agreement = RentalAgreement.objects.get(id=agreement_id)
    except Exception:
        return JsonResponse({'error': 'Not found'}, status=404)

    if not _check_access(agreement, mongo_user):
        return JsonResponse({'error': 'Access denied'}, status=403)

    pdf_exists = os.path.exists(_get_pdf_path(agreement_id))

    return JsonResponse({
        'status':          agreement.status,
        'tenant_signed':   agreement.tenant_signed,
        'owner_signed':    agreement.owner_signed,
        'both_signed':     agreement.both_signed(),
        'tenant_signed_at': agreement.tenant_signed_at.strftime('%d %b %Y, %I:%M %p') if agreement.tenant_signed_at else None,
        'owner_signed_at':  agreement.owner_signed_at.strftime('%d %b %Y, %I:%M %p')  if agreement.owner_signed_at  else None,
        'pdf_exists':      pdf_exists,
        'pdf_url':         agreement.pdf_url or '',
    })