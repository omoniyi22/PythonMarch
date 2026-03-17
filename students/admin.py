from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Department, Student, Course, Enrollment

class StudentAdmin(UserAdmin):
    list_display = ['student_id', 'email', 'first_name', 'last_name', 'department', 'is_active']
    list_filter = ['department', 'is_active', 'enrollment_date']
    search_fields = ['student_id', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Student Info', {
            'fields': ('student_id', 'phone_number', 'address', 'date_of_birth',
                      'department', 'enrollment_date', 'graduation_date')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Student Info', {
            'fields': ('student_id', 'email', 'first_name', 'last_name', 
                      'department', 'phone_number')
        }),
    )

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'department', 'instructor', 'semester']
    list_filter = ['department', 'semester', 'credits']
    search_fields = ['code', 'name', 'instructor']
    inlines = [EnrollmentInline]

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'established_date']
    search_fields = ['code', 'name']

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrollment_date', 'grade']
    list_filter = ['grade', 'course__department', 'enrollment_date']
    search_fields = ['student__first_name', 'student__last_name', 'course__name']

# Register your models
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)