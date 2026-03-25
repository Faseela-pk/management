from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Department, Staff, Student

class StudentSignUpForm(UserCreationForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'Student'
        if commit:
            user.save()
            Student.objects.create(user=user, department=self.cleaned_data.get('department'))
        return user

class StaffSignUpForm(UserCreationForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'Staff'
        user.is_staff = True
        if commit:
            user.save()
            Staff.objects.create(user=user, department=self.cleaned_data.get('department'))
        return user

class AdminSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'Admin'
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['department']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['department', 'assigned_staff']

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'profile_picture')
