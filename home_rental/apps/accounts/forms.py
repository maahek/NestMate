"""
NestMate — Account Forms
Registration, Login, Profile Edit, Verification Upload
"""

from django import forms


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRATION FORM
# ══════════════════════════════════════════════════════════════════════════════

class RegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class':       'form-control',
            'placeholder': 'Your full name',
        })
    )
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class':       'form-control',
            'placeholder': 'Choose a username',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class':       'form-control',
            'placeholder': 'your@email.com',
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class':       'form-control',
            'placeholder': '+91 9876543210',
        })
    )
    role = forms.ChoiceField(
        choices=[
            ('tenant', '🔍 I am looking to rent'),
            ('owner',  '🏠 I want to list my property'),
            ('both',   '🔄 Both'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'role-radio'})
    )
    city = forms.ChoiceField(
        choices=[
            ('', 'Select your city'),
            ('Mumbai',    'Mumbai'),
            ('Pune',      'Pune'),
            ('Bangalore', 'Bangalore'),
            ('Delhi',     'Delhi'),
            ('Hyderabad', 'Hyderabad'),
            ('Chennai',   'Chennai'),
            ('Kolkata',   'Kolkata'),
            ('Ahmedabad', 'Ahmedabad'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Min 8 characters',
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Repeat your password',
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip().lower()
        if len(username) < 3:
            raise forms.ValidationError('Username must be at least 3 characters.')
        if not username.replace('_', '').replace('.', '').isalnum():
            raise forms.ValidationError('Only letters, numbers, underscores, dots allowed.')
        # Check MongoDB for existing username
        from apps.accounts.models import User
        if User.objects(username=username).first():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        from apps.accounts.models import User
        if User.objects(email=email).first():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        pwd  = cleaned.get('password')
        cpwd = cleaned.get('confirm_password')
        if pwd and cpwd and pwd != cpwd:
            raise forms.ValidationError({'confirm_password': 'Passwords do not match.'})
        return cleaned


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN FORM
# ══════════════════════════════════════════════════════════════════════════════

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class':       'form-control',
            'placeholder': 'your@email.com',
            'autofocus':   True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Your password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE EDIT FORM
# ══════════════════════════════════════════════════════════════════════════════

class ProfileEditForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class':       'form-control',
            'placeholder': '+91 9876543210',
        })
    )
    bio = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class':       'form-control',
            'placeholder': 'Tell others about yourself...',
            'rows':        3,
        })
    )
    city = forms.ChoiceField(
        choices=[
            ('Mumbai',    'Mumbai'),
            ('Pune',      'Pune'),
            ('Bangalore', 'Bangalore'),
            ('Delhi',     'Delhi'),
            ('Hyderabad', 'Hyderabad'),
            ('Chennai',   'Chennai'),
            ('Kolkata',   'Kolkata'),
            ('Ahmedabad', 'Ahmedabad'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    locality = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class':       'form-control',
            'placeholder': 'e.g. Koramangala',
        })
    )
    role = forms.ChoiceField(
        choices=[
            ('tenant', '🔍 Looking to rent'),
            ('owner',  '🏠 Listing properties'),
            ('both',   '🔄 Both'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )


# ══════════════════════════════════════════════════════════════════════════════
# VERIFICATION UPLOAD FORM (Feature 2 — Trust Score)
# ══════════════════════════════════════════════════════════════════════════════

class VerificationForm(forms.Form):
    doc_type = forms.ChoiceField(
        label='Document Type',
        choices=[
            ('aadhaar',           '🪪 Aadhaar Card'),
            ('pan',               '🗂️ PAN Card'),
            ('passport',          '📘 Passport'),
            ('driving_license',   '🚗 Driving License'),
            ('electricity_bill',  '💡 Electricity Bill'),
            ('water_bill',        '💧 Water Bill'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    document_file = forms.FileField(
        label='Upload Document',
        widget=forms.FileInput(attrs={
            'class':  'form-control',
            'accept': 'image/*,application/pdf',
        })
    )

    def clean_document_file(self):
        file = self.cleaned_data.get('document_file')
        if file:
            # Max 5 MB
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File too large. Maximum size is 5 MB.')
            # Only images and PDFs
            allowed = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
            if file.content_type not in allowed:
                raise forms.ValidationError('Only JPG, PNG, or PDF files are allowed.')
        return file


# ══════════════════════════════════════════════════════════════════════════════
# CHANGE PASSWORD FORM
# ══════════════════════════════════════════════════════════════════════════════

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Current password',
        })
    )
    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'New password (min 8 characters)',
        })
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Repeat new password',
        })
    )

    def clean(self):
        cleaned = super().clean()
        new_pwd  = cleaned.get('new_password')
        conf_pwd = cleaned.get('confirm_new_password')
        if new_pwd and conf_pwd and new_pwd != conf_pwd:
            raise forms.ValidationError({
                'confirm_new_password': 'New passwords do not match.'
            })
        return cleaned