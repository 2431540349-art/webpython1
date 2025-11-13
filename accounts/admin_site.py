"""Custom admin site with Vietnamese translations and enhanced styling."""
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class VietnameseAdminSite(AdminSite):
    # Thay đổi tiêu đề trang admin
    site_title = _('Quản Trị Website')
    site_header = _('Hệ Thống Quản Trị')
    index_title = _('Bảng Điều Khiển')
    
    def each_context(self, request):
        context = super().each_context(request)
        context['custom_css'] = 'accounts/admin/css/custom_admin.css'
        return context

# Tạo instance mới cho admin site
admin_site = VietnameseAdminSite(name='vietnamese_admin')