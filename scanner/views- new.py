# scanner/views.py — FINAL, CLEAN & OPTIMAL
import json
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from .models import ScanResult
from users.models import FirmProfile
from .tasks import run_compliance_scan



# ----------------------------------------------------------------------
# Helper – safe firm access
# ----------------------------------------------------------------------
def get_firm(request):
    return request.user.firmprofile


# ----------------------------------------------------------------------
# 1. Dashboard (root /scanner/)
# ----------------------------------------------------------------------
class ScannerDashboardView(LoginRequiredMixin, ListView):
    template_name = "scanner/dashboard.html"
    context_object_name = "scans"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        try:
            get_firm(request)
        except FirmProfile.DoesNotExist:
            if request.htmx:
                return self._htmx_no_firm()
            messages.warning(request, "Please set up your firm first.")
            return redirect(reverse("firm_settings"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return ScanResult.objects.filter(firm=get_firm(self.request))

    def _htmx_no_firm(self):
        html = render_to_string(
            "scanner/partials/no_firm.html",
            {"firm_settings_url": reverse("firm_settings")},
            request=self.request,
        )
        resp = HttpResponse(html)
        resp["HX-Retarget"] = "body"
        resp["HX-Reswap"] = "innerHTML"
        return resp


# ----------------------------------------------------------------------
# 2. Scan List
# ----------------------------------------------------------------------
class ScanListView(LoginRequiredMixin, ListView):
    model = ScanResult
    template_name = "scanner/scan_list.html"
    context_object_name = "scans"
    paginate_by = 15

    def dispatch(self, request, *args, **kwargs):
        try:
            get_firm(request)
        except FirmProfile.DoesNotExist:
            if request.htmx:
                return self._htmx_no_firm()
            messages.warning(request, "Please set up your firm first.")
            return redirect(reverse("firm_settings"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return ScanResult.objects.filter(firm=get_firm(self.request))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx["total_scans"] = qs.count()
        latest = qs.first()
        ctx["latest_grade"] = latest.grade if latest else None
        return ctx

    def _htmx_no_firm(self):
        html = render_to_string(
            "scanner/partials/no_firm.html",
            {"firm_settings_url": reverse("firm_settings")},
            request=self.request,
        )
        resp = HttpResponse(html)
        resp["HX-Retarget"] = "body"
        resp["HX-Reswap"] = "innerHTML"
        return resp


# ----------------------------------------------------------------------
# 3. Modal – GET (HTMX)
# ----------------------------------------------------------------------
class StartScanModalView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'scanner/partials/run_scan_modal.html')


# ----------------------------------------------------------------------
# 4. Start Scan – POST (rate-limited)
# ----------------------------------------------------------------------
@ratelimit(key='user', rate='3/m', method='POST', block=True)
def start_scan_view(request):
    if request.method != 'POST':
        return redirect('scanner:scan_list')

    domain = request.POST.get('domain', '').strip()
    if not domain:
        messages.error(request, "Domain is required.")
        return redirect('scanner:scan_list')

    scan = ScanResult.objects.create(
        firm=get_firm(request),
        domain=domain,
        status='pending'
    )
    run_compliance_scan.delay(scan.id)
    messages.success(request, f"Scan started for {domain}")

    if request.htmx:
        scans = ScanResult.objects.filter(firm=get_firm(request)).order_by('-scan_date')
        return render(request, 'scanner/partials/scan_list_table.html', {'scans': scans})

    return redirect('scanner:scan_status', scan.id)


# ----------------------------------------------------------------------
# 5. Status partial (polling)
# ----------------------------------------------------------------------
def scan_status_partial(request, pk):
    scan = get_object_or_404(ScanResult, pk=pk, firm=get_firm(request))
    return render(request, 'scanner/partials/scan_progress.html', {'scan': scan})


# ----------------------------------------------------------------------
# 6. Scan Status Page
# ----------------------------------------------------------------------
class ScanStatusView(LoginRequiredMixin, DetailView):
    model = ScanResult
    template_name = 'scanner/scan_status.html'
    context_object_name = 'scan'

    def get_queryset(self):
        return ScanResult.objects.filter(firm=self.request.user.firmprofile)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if request.htmx:
            return render(request, 'scanner/partials/scan_progress.html', context)
        return self.render_to_response(context)


# ----------------------------------------------------------------------
# 7. PDF Generation (function)
# ----------------------------------------------------------------------
def generate_pdf(request, pk):
    scan = get_object_or_404(ScanResult, pk=pk, firm=get_firm(request))
    # TODO: Implement real PDF generation (WeasyPrint, ReportLab, etc.)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="compliance_scan_{pk}.pdf"'
    response.write("PDF generation stub – implement with WeasyPrint or ReportLab")
    return response


# ----------------------------------------------------------------------
# 8. Cancel / Retry
# ----------------------------------------------------------------------
class CancelScanView(LoginRequiredMixin, View):
    def post(self, request, pk):
        scan = get_object_or_404(ScanResult, pk=pk, firm=get_firm(request))
        scan.status = 'cancelled'
        scan.save()
        return redirect('scanner:scan_status', pk)


class RetryScanView(LoginRequiredMixin, View):
    def post(self, request, pk):
        scan = get_object_or_404(ScanResult, pk=pk, firm=get_firm(request))
        scan.status = 'pending'
        scan.progress = 0
        scan.scan_log = ""
        scan.save()
        run_compliance_scan.delay(scan.id)
        return redirect('scanner:scan_status', pk)
        
