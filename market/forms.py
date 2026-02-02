# d:\Grambazaar\grambazaar\market\forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import SHG, Product, Order, BuyerProfile, DigiCourse, ProductReview


class SHGRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    
    class Meta:
        model = SHG
        fields = ['name', 'contact_person', 'phone', 'email', 'state', 'city', 'description', 'logo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        text_like_fields = [
            'username', 'password', 'confirm_password',
            'name', 'contact_person', 'phone', 'email',
            'city', 'state',
        ]
        for name in text_like_fields:
            if name in self.fields:
                existing = self.fields[name].widget.attrs.get('class', '')
                css_class = (existing + ' form-control').strip() if existing else 'form-control'
                self.fields[name].widget.attrs['class'] = css_class

        # Description textarea
        if 'description' in self.fields:
            existing = self.fields['description'].widget.attrs.get('class', '')
            css_class = (existing + ' form-control').strip() if existing else 'form-control'
            self.fields['description'].widget.attrs['class'] = css_class
            if isinstance(self.fields['description'].widget, forms.Textarea):
                self.fields['description'].widget.attrs.setdefault('rows', 3)

        # Logo file input
        if 'logo' in self.fields:
            existing = self.fields['logo'].widget.attrs.get('class', '')
            css_class = (existing + ' form-control').strip() if existing else 'form-control'
            self.fields['logo'].widget.attrs['class'] = css_class
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email


class ProductSubmissionForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category', 'image', 'inventory']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Text inputs
        for name in ['title', 'price', 'inventory']:
            if name in self.fields:
                self.fields[name].widget.attrs.update({'class': 'form-control'})

        # Description textarea
        if 'description' in self.fields:
            self.fields['description'].widget.attrs.update({
                'class': 'form-control',
                'rows': self.fields['description'].widget.attrs.get('rows', 4),
            })

        # Category select
        if 'category' in self.fields:
            self.fields['category'].widget.attrs.update({'class': 'form-select'})

        # Image file input
        if 'image' in self.fields:
            # Use form-control for consistent Bootstrap styling of file input
            self.fields['image'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True, shg=None):
        product = super().save(commit=False)
        if shg:
            product.shg = shg
        product.status = 'pending'
        if commit:
            product.save()
        return product


class BuyerOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['buyer_name', 'buyer_contact', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ['buyer_name', 'buyer_contact', 'address']:
            if name in self.fields:
                css_class = 'form-control'
                existing = self.fields[name].widget.attrs.get('class', '')
                if existing:
                    css_class = existing + ' ' + css_class
                self.fields[name].widget.attrs['class'] = css_class
    
    def save(self, commit=True, product=None):
        order = super().save(commit=False)
        if product:
            order.product = product
            order.amount = product.price
        if commit:
            order.save()
        return order


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid username or password")
        
        return cleaned_data


class AdminProductForm(forms.ModelForm):
    shg = forms.ModelChoiceField(queryset=SHG.objects.all())
    image = forms.ImageField(required=False)

    class Meta:
        model = Product
        fields = ['shg', 'title', 'description', 'price', 'category', 'inventory', 'image', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Text inputs
        for name in ['title', 'price', 'inventory']:
            if name in self.fields:
                self.fields[name].widget.attrs.update({'class': 'form-control'})

        # SHG, category, status selects
        for name in ['shg', 'category', 'status']:
            if name in self.fields:
                self.fields[name].widget.attrs.update({'class': 'form-select'})

        # Image file input
        if 'image' in self.fields:
            existing = self.fields['image'].widget.attrs.get('class', '')
            css_class = (existing + ' form-control').strip() if existing else 'form-control'
            self.fields['image'].widget.attrs['class'] = css_class


class BuyerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    address = forms.CharField(widget=forms.Textarea, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    pincode = forms.CharField(max_length=10, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 
                 'first_name', 'last_name', 'phone', 'address', 
                 'city', 'state', 'pincode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        text_fields = [
            'username', 'email', 'password1', 'password2',
            'first_name', 'last_name', 'phone',
            'city', 'state', 'pincode',
        ]
        for name in text_fields:
            if name in self.fields:
                existing = self.fields[name].widget.attrs.get('class', '')
                css_class = (existing + ' form-control').strip() if existing else 'form-control'
                self.fields[name].widget.attrs['class'] = css_class

        if 'address' in self.fields:
            widget = self.fields['address'].widget
            existing = widget.attrs.get('class', '')
            css_class = (existing + ' form-control').strip() if existing else 'form-control'
            widget.attrs['class'] = css_class
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 3)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email


class BuyerLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            css_class = (existing + ' form-control').strip() if existing else 'form-control'
            field.widget.attrs['class'] = css_class


class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        fields = ['phone', 'address', 'city', 'state', 'pincode']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            css_class = (existing + ' form-control').strip() if existing else 'form-control'
            field.widget.attrs['class'] = css_class


class DigiCourseForm(forms.ModelForm):
    class Meta:
        model = DigiCourse
        fields = ['title', 'language', 'video_url', 'description', 'duration_minutes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Text inputs
        for name in ['title', 'video_url', 'duration_minutes']:
            if name in self.fields:
                existing = self.fields[name].widget.attrs.get('class', '')
                css_class = (existing + ' form-control').strip() if existing else 'form-control'
                self.fields[name].widget.attrs['class'] = css_class

        # Language select
        if 'language' in self.fields:
            existing = self.fields['language'].widget.attrs.get('class', '')
            css_class = (existing + ' form-select').strip() if existing else 'form-select'
            self.fields['language'].widget.attrs['class'] = css_class

        # Description textarea
        if 'description' in self.fields:
            widget = self.fields['description'].widget
            existing = widget.attrs.get('class', '')
            css_class = (existing + ' form-control').strip() if existing else 'form-control'
            widget.attrs['class'] = css_class
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 3)


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'rating' in self.fields:
            existing = self.fields['rating'].widget.attrs.get('class', '')
            css_class = (existing + ' form-select').strip() if existing else 'form-select'
            self.fields['rating'].widget.attrs['class'] = css_class

        if 'comment' in self.fields:
            widget = self.fields['comment'].widget
            existing = widget.attrs.get('class', '')
            css_class = (existing + ' form-control').strip() if existing else 'form-control'
            widget.attrs['class'] = css_class
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 3)