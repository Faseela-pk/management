from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, Department, Staff, Student
from .forms import StudentSignUpForm, StaffSignUpForm, DepartmentForm, StaffForm, StudentForm, UserProfileUpdateForm
from .decorators import admin_required, staff_required, student_required

# Function-Based Views (FBVs) are used throughout the application to demonstrate explicit logic and authorization handling.

# Application Entry Point
def index(request):
    if request.user.is_authenticated:
        if request.user.role == 'Admin' or request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.role == 'Staff':
            return redirect('staff_dashboard')
        else:
            return redirect('student_dashboard')
    return redirect('login')

# --- Authentication Views ---
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to the Student Portal!")
            return redirect('student_dashboard')
    else:
        form = StudentSignUpForm()
    return render(request, 'core/register.html', {'form': form, 'title': 'Student Registration'})

# --- Dashboards ---
@login_required
@admin_required
def admin_dashboard(request):
    context = {
        'staff_count': Staff.objects.count(),
        'student_count': Student.objects.count(),
        'dept_count': Department.objects.count(),
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
@staff_required
def staff_dashboard(request):
    # Depending on role, handle the display
    if request.user.role == 'Staff' and hasattr(request.user, 'staff_profile'):
        students = Student.objects.filter(department=request.user.staff_profile.department)
    elif request.user.role == 'Admin' or request.user.is_superuser:
        students = Student.objects.all()
    else:
        students = Student.objects.none()
    
    return render(request, 'core/staff_dashboard.html', {'students': students})

@login_required
@student_required
def student_dashboard(request):
    try:
        student_profile = request.user.student_profile
    except Student.DoesNotExist:
        student_profile = None
    return render(request, 'core/student_dashboard.html', {'student_profile': student_profile})

# --- Profile View ---
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form, 'user': request.user})

# --- CRUD for Department (Admin only) ---
@login_required
@admin_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'core/department_list.html', {'departments': departments})

@login_required
@admin_required
def department_create(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Department created successfully.")
        return redirect('department_list')
    return render(request, 'core/form_template.html', {'form': form, 'title': 'Create Department'})

@login_required
@admin_required
def department_update(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=dept)
    if form.is_valid():
        form.save()
        messages.success(request, "Department updated successfully.")
        return redirect('department_list')
    return render(request, 'core/form_template.html', {'form': form, 'title': f'Update Department: {dept.name}'})

@login_required
@admin_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, "Department deleted successfully.")
        return redirect('department_list')
    return render(request, 'core/confirm_delete.html', {'object': dept, 'title': 'Delete Department'})

# --- CRUD for Staff (Admin only) ---
@login_required
@admin_required
def staff_list(request):
    staffs = Staff.objects.all()
    return render(request, 'core/staff_list.html', {'staffs': staffs})

@login_required
@admin_required
def staff_create(request):
    if request.method == 'POST':
        user_form = StaffSignUpForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Staff member created successfully.")
            return redirect('staff_list')
    else:
        user_form = StaffSignUpForm()
    return render(request, 'core/form_template.html', {'form': user_form, 'title': 'Create Staff Member'})

@login_required
@admin_required
def staff_update(request, pk):
    staff_member = get_object_or_404(Staff, user__pk=pk)
    form = StaffForm(request.POST or None, instance=staff_member)
    if form.is_valid():
        form.save()
        messages.success(request, "Staff profile updated successfully.")
        return redirect('staff_list')
    return render(request, 'core/form_template.html', {'form': form, 'title': f'Update Staff: {staff_member.user.username}'})

@login_required
@admin_required
def staff_delete(request, pk):
    staff_member = get_object_or_404(Staff, user__pk=pk)
    if request.method == 'POST':
        staff_member.user.delete() # Deletes user + Staff profile
        messages.success(request, "Staff member deleted successfully.")
        return redirect('staff_list')
    return render(request, 'core/confirm_delete.html', {'object': staff_member, 'title': 'Delete Staff'})

# --- CRUD for Students (Staff and Admin) ---
@login_required
@staff_required
def student_list(request):
    if request.user.role == 'Admin' or request.user.is_superuser:
        students = Student.objects.all()
    else:
        students = Student.objects.filter(department=request.user.staff_profile.department)
    return render(request, 'core/student_list.html', {'students': students})

@login_required
@staff_required
def student_create(request):
    if request.method == 'POST':
        user_form = StudentSignUpForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Student created successfully.")
            return redirect('student_list')
    else:
        user_form = StudentSignUpForm()
    return render(request, 'core/form_template.html', {'form': user_form, 'title': 'Create Student'})

@login_required
@staff_required
def student_update(request, pk):
    student = get_object_or_404(Student, user__pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, "Student profile updated successfully.")
        return redirect('student_list')
    return render(request, 'core/form_template.html', {'form': form, 'title': f'Update Student: {student.user.username}'})

@login_required
@staff_required
def student_delete(request, pk):
    student = get_object_or_404(Student, user__pk=pk)
    if request.method == 'POST':
        student.user.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect('student_list')
    return render(request, 'core/confirm_delete.html', {'object': student, 'title': 'Delete Student'})
