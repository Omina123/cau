
from django.shortcuts import render,redirect, get_object_or_404

from django.db.models import Prefetch
from .forms import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date
from django.template.loader import get_template
#from xhtml2pdf import pisa
from django.http import HttpResponse


from django.contrib import messages
def home (request):
    return render(request, 'home.html')
# Create your views here.
def  about(request):
    return render(request, 'about.html')
def  Contact(request):
    return render(request, 'Contact.html')
def register_member(request):
    form = MemberForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request,"Registered Member succefully")
            return redirect('register_member')  # You can also redirect to a success page or the member list page after saving
            # redirect to members page or success message
    context = {'form': form}
    return render(request, 'register_member.html', context)

def jumuiya(request):
    if request.method == 'POST':
        form = JumuiyaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Jumuiya recorded successfully!")
            return redirect('jumuiya')
    else:
        form = JumuiyaForm()   

    context = {
        'form': form
    }
    return render(request, 'jumuiya.html', context)
@login_required(login_url='Login')
def out_station(request):
    if request.method == 'POST':
        form = OutstationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Outstation recorded successfully')
            return redirect('out_station')
    else:
        form = OutstationForm()   

    context = {
        'form': form
    }
    return render(request, 'outstation.html', context)
# AJAX view for Outstations
@login_required(login_url='Login')
def load_outstations(request):
    parish = request.GET.get('parish')
    outstations = Outstation.objects.filter(parish=parish).order_by('name')
    return JsonResponse(list(outstations.values('id','name')), safe=False)

# AJAX view for Jumuiya
@login_required(login_url='Login')
def load_jumuiya(request):
    outstation_id = request.GET.get('outstation')
    jumuiya = Jumuiya.objects.filter(outstation_id=outstation_id).order_by('name')
    return JsonResponse(list(jumuiya.values('id','name')), safe=False)


@login_required(login_url='Login')
def zaka(request):

    members = Member.objects.select_related('outstation', 'jumuiya').all()

    # FILTERING
    outstation_id = request.GET.get('outstation')
    jumuiya_id = request.GET.get('jumuiya')

    if outstation_id:
        members = members.filter(outstation_id=outstation_id)

    if jumuiya_id:
        members = members.filter(jumuiya_id=jumuiya_id)

    # SAVE BULK ZAKA
    if request.method == "POST":

        month = request.POST.get("month")
        year = request.POST.get("year")
        amount = request.POST.get("amount")
        selected_members = request.POST.getlist("members")

        if not selected_members:
            messages.error(request, "Please select at least one member.")
            return redirect('zaka')

        for member_id in selected_members:
            if not Zaka.objects.filter(
                member_id=member_id,
                month=month,
                year=year
            ).exists():

                Zaka.objects.create(
                    member_id=member_id,
                    month=month,
                    year=year,
                    amount=amount
                )

        messages.success(request, "Monthly Mavuno recorded successfully!")
        return redirect('zaka')

    context = {
        "members": members,
        "outstations": Outstation.objects.all(),
        "jumuiyas": Jumuiya.objects.all(),
    }

    return render(request, "zaka.html", context)
def mavuno(request):

    # Filters
    outstation_id = request.GET.get('outstation')
    jumuiya_id = request.GET.get('jumuiya')

    members = Member.objects.all()

    if outstation_id:
        members = members.filter(outstation_id=outstation_id)

    if jumuiya_id:
        members = members.filter(jumuiya_id=jumuiya_id)

    # Handle POST (Bulk Save)
    if request.method == "POST":

        produce_type = request.POST.get('produce_type')
        quantity = request.POST.get('quantity')
        selected_members = request.POST.getlist('members')

        if not selected_members:
            messages.error(request, "Please select at least one member.")
            return redirect('mavuno')

        for member_id in selected_members:
            Mavuno.objects.create(
                member_id=member_id,
                produce_type=produce_type,
                quantity=quantity,
                date_recorded=date.today()
            )

        messages.success(request, "Mavuno recorded successfully!")
        return redirect('mavuno')

    context = {
        'members': members,
        'outstations': Outstation.objects.all(),
        'jumuiyas': Jumuiya.objects.all(),
    }

    return render(request, 'mavuno.html', context)
@login_required(login_url='Login')
def Special(request):

    # Filters
    outstation_id = request.GET.get('outstation')
    jumuiya_id = request.GET.get('jumuiya')

    members = Member.objects.all()

    if outstation_id:
        members = members.filter(outstation_id=outstation_id)

    if jumuiya_id:
        members = members.filter(jumuiya_id=jumuiya_id)

    # Handle Bulk POST
    if request.method == "POST":

        contribution_type = request.POST.get('contribution_type')
        amount = request.POST.get('amount')
        selected_members = request.POST.getlist('members')

        if not selected_members:
            messages.error(request, "Please select at least one member.")
            return redirect('Special')

        if float(amount) < 100:
            messages.error(request, "Amount must be 100 or above.")
            return redirect('Special')

        for member_id in selected_members:
            SpecialContribution.objects.create(
                member_id=member_id,
                contribution_type=contribution_type,
                amount=amount,
                date_recorded=date.today()
            )

        messages.success(request, "Special Contribution recorded successfully!")
        return redirect('Special')

    context = {
        'members': members,
        'outstations': Outstation.objects.all(),
        'jumuiyas': Jumuiya.objects.all(),
    }

    return render(request, 'special.html', context)
@login_required(login_url='Login')
def Dashbd(request):
    outstations = Outstation.objects.all()
    outstation_data = []
    current_year = date.today().year

    # Parish-wide totals
    parish_totals = {
        'sadaka': 0,
        'mavuno': {p: 0 for p in ['MAIZE','BEANS','WHEAT','MILLET','COW','GOAT','SHEEP','CHICKEN','MONEY','OTHER']},
        'special': {'ASSUMPTION': 0, 'CHRISTMAS': 0, 'PASAKA': 0},
        'zaka': 0,
        'pledge': 0,
        'jumuiya': 0
    }

    for outstation in outstations:
        # Sadaka totals
        sadaka_weekly = Sadaka.objects.filter(outstation=outstation).order_by('-date_recorded')[:5]
        sadaka_yearly = Sadaka.objects.filter(
            outstation=outstation,
            date_recorded__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        parish_totals['sadaka'] += sadaka_yearly

        # Mavuno totals per produce
        mavuno_totals = {}
        for produce in ['MAIZE','BEANS','WHEAT','MILLET','COW','GOAT','SHEEP','CHICKEN','MONEY','OTHER']:
            total = Mavuno.objects.filter(
                member__outstation=outstation,
                produce_type=produce,
                date_recorded__year=current_year
            ).aggregate(total=Sum('quantity'))['total'] or 0
            mavuno_totals[produce] = total
            parish_totals['mavuno'][produce] += total

        # Special contributions totals
        special_totals = {}
        for contrib in ['ASSUMPTION','CHRISTMAS','PASAKA']:
            total = SpecialContribution.objects.filter(
                member__outstation=outstation,
                contribution_type=contrib,
                date_recorded__year=current_year
            ).aggregate(total=Sum('amount'))['total'] or 0
            special_totals[contrib] = total
            parish_totals['special'][contrib] += total

        # Zaka totals
        zaka_total = Zaka.objects.filter(
            member__outstation=outstation,
            date_recorded__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        parish_totals['zaka'] += zaka_total
        zaka_totals = {'current_year': zaka_total}

        # Pledge totals
        pledge_total = Pledge.objects.filter(
            member__outstation=outstation,
            date_pledged__year=current_year
        ).aggregate(total=Sum('pledged_amount'))['total'] or 0
        parish_totals['pledge'] += pledge_total

        # JumuiyaContribution totals
        jumuiya_total = JumuiyaContribution.objects.filter(
            jumuiya__outstation=outstation,
            date_recorded__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        parish_totals['jumuiya'] += jumuiya_total

        outstation_data.append({
            'outstation': outstation,
            'sadaka_weekly': sadaka_weekly,
            'sadaka_yearly': sadaka_yearly,
            'mavuno_totals': mavuno_totals,
            'special_totals': special_totals,
            'zaka_totals': zaka_totals,
            'pledge_total': pledge_total,
            'jumuiya_total': jumuiya_total,
        })

    context = {
        'outstation_data': outstation_data,
        'parish_totals': parish_totals,
        'now': date.today()
    }

    return render(request, 'dash.html', context)


@login_required(login_url='Login')


def outstation(request, pk):
    outstation = get_object_or_404(Outstation, id=pk)
    members = Member.objects.filter(outstation=outstation)

    member_data = []

    for member in members:

        # -------------------------
        # ZAKA (Grouped by Month)
        # -------------------------
        zaka_qs = Zaka.objects.filter(member=member).order_by('date_recorded')

        # Automatically generate dictionary from model choices
        zaka = {key: [] for key, _ in Zaka.MONTH_CHOICES}

        for z in zaka_qs:
            if z.month in zaka:   # Safety check
                zaka[z.month].append({
                    'amount': z.amount,
                    'year': z.year,
                    'date': z.date_recorded,
                })

        # -------------------------
        # SPECIAL CONTRIBUTIONS
        # -------------------------
        special_qs = SpecialContribution.objects.filter(member=member).order_by('date_recorded')

        special = {key: [] for key, _ in SpecialContribution.CONTRIBUTION_TYPE}

        for s in special_qs:
            if s.contribution_type in special:   # Safety check
                special[s.contribution_type].append({
                    'amount': s.amount,
                    'date': s.date_recorded,
                    'year': s.date_recorded.year,
                })

        # -------------------------
        # MAVUNO (Produce)
        # -------------------------
        mavuno_qs = Mavuno.objects.filter(member=member).order_by('date_recorded')

        mavuno = {key: [] for key, _ in Mavuno.PRODUCE_CHOICES}

        for p in mavuno_qs:
            if p.produce_type in mavuno:   # Safety check
                mavuno[p.produce_type].append({
                    'quantity': p.quantity,
                    'date': p.date_recorded,
                    'year': p.date_recorded.year,
                })

        # -------------------------
        # APPEND MEMBER DATA
        # -------------------------
        member_data.append({
            'member': member,
            'zaka': zaka,
            'special': special,
            'mavuno': mavuno,
        })

    context = {
        'outstation': outstation,
        'outstation_name': outstation.name,
        'member_data': member_data,
    }

    return render(request, 'detail.html', context)
@login_required(login_url='Login')
def sadaka(request):

    outstations = Outstation.objects.all()
    sadaka_list = Sadaka.objects.order_by('-date_recorded')

    if request.method == "POST":

        outstation_id = request.POST.get('outstation')
        amount = request.POST.get('amount')

        if not outstation_id:
            messages.error(request, "Please select an outstation.")
            return redirect('sadaka')

        if float(amount) <= 0:
            messages.error(request, "Amount must be greater than 0.")
            return redirect('sadaka')

        Sadaka.objects.create(
            outstation_id=outstation_id,
            amount=amount,
            date_recorded=date.today()
        )

        messages.success(request, "Sadaka recorded successfully!")
        return redirect('sadaka')

    context = {
        'outstations': outstations,
        'sadaka_list': sadaka_list
    }

    return render(request, 'sdk.html', context)

def Gallary(request):
    # Example photo list; replace with actual media files
    photos = [
        {'url': '/static/images/event1.jpg', 'title': 'Christmas Celebration', 'alt': 'Christmas'},
        {'url': '/static/images/event2.jpg', 'title': 'Youth Gathering', 'alt': 'Youth'},
        {'url': '/static/images/event3.jpg', 'title': 'Easter Service', 'alt': 'Easter'},
    ]
    return render(request, 'gallary.html', {'photos': photos})
def jumuiya_contribution(request):

    jumuiyas = Jumuiya.objects.all()
    contributions = JumuiyaContribution.objects.order_by('-date_recorded')

    if request.method == "POST":

        jumuiya_id = request.POST.get('jumuiya')
        year = request.POST.get('year')
        amount = request.POST.get('amount')

        if not jumuiya_id:
            messages.error(request, "Please select a Jumuiya.")
            return redirect('jumuiya_contribution')

        if float(amount) < 20000:
            messages.error(request, "Amount must be 20,000 or above.")
            return redirect('jumuiya_contribution')

        # Optional: Prevent duplicate year entry
        if JumuiyaContribution.objects.filter(
            jumuiya_id=jumuiya_id,
            year=year
        ).exists():
            messages.error(request, "Contribution for this Jumuiya and year already exists.")
            return redirect('jumuiya_contribution')

        JumuiyaContribution.objects.create(
            jumuiya_id=jumuiya_id,
            year=year,
            amount=amount,
            date_recorded=date.today()
        )

        messages.success(request, "Jumuiya Contribution recorded successfully!")
        return redirect('jumuiya_contribution')

    context = {
        'jumuiyas': jumuiyas,
        'contributions': contributions
    }

    return render(request, 'jumuiya_contribution.html', context)

def pledge_view(request):
    members = Member.objects.all()
    pledges = Pledge.objects.order_by('-date_pledged')

    if request.method == "POST":
        member_id = request.POST.get('member')
        purpose = request.POST.get('purpose')
        pledged_amount = request.POST.get('pledged_amount')
        amount_paid = request.POST.get('amount_paid') or 0
        due_date = request.POST.get('due_date')

        if not member_id:
            messages.error(request, "Please select a member.")
            return redirect('pledge_view')

        if float(pledged_amount) < 1:
            messages.error(request, "Pledged amount must be at least 1.")
            return redirect('pledge_view')

        Pledge.objects.create(
            member_id=member_id,
            purpose=purpose,
            pledged_amount=pledged_amount,
            amount_paid=amount_paid,
            date_pledged=date.today(),
            due_date=due_date or None
        )

        messages.success(request, "Pledge recorded successfully!")
        return redirect('pledge_view')

    context = {
        'members': members,
        'pledges': pledges,
    }

    return render(request, 'pledge.html', context)


# def mavuno_pdf_report(request):
#     current_year = date.today().year
#     outstations = Outstation.objects.all()

#     PRODUCE_TYPES = ['MAIZE','BEANS','WHEAT','MILLET','SHEEP','COW','GOAT','CHICKEN','OTHER']

#     report_data = []

#     # GRAND TOTAL HOLDER
#     grand_totals = {
#         'MONEY': {'pledged': 0, 'paid': 0}
#     }
#     for produce in PRODUCE_TYPES:
#         grand_totals[produce] = {'pledged': 0, 'paid': 0}

#     # LOOP OUTSTATIONS
#     for outstation in outstations:
#         jumuiyas = Jumuiya.objects.filter(outstation=outstation)

#         jumuiya_data = []

#         # OUTSTATION SUBTOTAL HOLDER
#         outstation_totals = {
#             'MONEY': {'pledged': 0, 'paid': 0}
#         }
#         for produce in PRODUCE_TYPES:
#             outstation_totals[produce] = {'pledged': 0, 'paid': 0}

#         # LOOP JUMUIYA
#         for jumuiya in jumuiyas:
#             row = {'jumuiya': jumuiya.name}

#             # ---------------- MONEY ----------------
#             pledges = Pledge.objects.filter(
#                 member__jumuiya=jumuiya,
#                 date_pledged__year=current_year
#             )

#             pledged_total = sum(p.pledged_amount for p in pledges)
#             paid_total = sum(p.amount_paid for p in pledges)

#             row['MONEY'] = {
#                 'pledged': pledged_total,
#                 'paid': paid_total
#             }

#             # Add to outstation subtotal
#             outstation_totals['MONEY']['pledged'] += pledged_total
#             outstation_totals['MONEY']['paid'] += paid_total

#             # Add to grand total
#             grand_totals['MONEY']['pledged'] += pledged_total
#             grand_totals['MONEY']['paid'] += paid_total


#             # ---------------- PRODUCE ----------------
#             for produce in PRODUCE_TYPES:
#                 produce_entries = Mavuno.objects.filter(
#                     member__jumuiya=jumuiya,
#                     produce_type=produce,
#                     date_recorded__year=current_year
#                 )

#                 pledged = sum(e.quantity for e in produce_entries)
#                 paid = pledged  # adjust if you separate paid later

#                 row[produce] = {
#                     'pledged': pledged,
#                     'paid': paid
#                 }

#                 # Add to outstation subtotal
#                 outstation_totals[produce]['pledged'] += pledged
#                 outstation_totals[produce]['paid'] += paid

#                 # Add to grand total
#                 grand_totals[produce]['pledged'] += pledged
#                 grand_totals[produce]['paid'] += paid

#             jumuiya_data.append(row)

#         report_data.append({
#             'outstation': outstation.name,
#             'jumuiyas': jumuiya_data,
#             'subtotal': outstation_totals   # ✅ OUTSTATION SUBTOTAL
#         })

#     context = {
#         'parish_name': 'ST PETERS NGOISA PARISH',
#         'year': current_year,
#         'report_data': report_data,
#         'grand_total': grand_totals   # ✅ PARISH GRAND TOTAL
#     }

#     template_path = 'mavuno_pdf.html'
#     template = get_template(template_path)
#     html = template.render(context)

#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'inline; filename="Mavuno_Report_{current_year}.pdf"'

#     pisa_status = pisa.CreatePDF(html, dest=response)

#     if pisa_status.err:
#         return HttpResponse('Error generating PDF <pre>' + html + '</pre>')

    return response
def stations(request):
    return render(request, 'stations.html')
def groups(request):
    return render(request, 'groups.html')
from django.db.models import Prefetch

def zakao(request, outstation_id):
    outstation = get_object_or_404(Outstation, id=outstation_id)
    selected_year = int(request.GET.get('year', date.today().year))
    
    months_list = [
        ('JAN', 'Jan'), ('FEB', 'Feb'), ('MAR', 'Mar'), ('APR', 'Apr'), 
        ('MAY', 'May'), ('JUN', 'Jun'), ('JUL', 'Jul'), ('AUG', 'Aug'), 
        ('SEP', 'Sep'), ('OCT', 'Oct'), ('NOV', 'Nov'), ('DEC', 'Dec')
    ]

    # Optimization: Prefetch all zaka for this year in ONE go
    zaka_qs = Zaka.objects.filter(year=selected_year)
    members = Member.objects.filter(outstation=outstation)\
                    .select_related('jumuiya')\
                    .prefetch_related(Prefetch('zaka_set', queryset=zaka_qs, to_attr='yearly_zaka'))
    
    report_data = []
    for member in members:
        # Now we look at the 'yearly_zaka' list we already fetched
        zaka_map = {z.month: z.amount for z in member.yearly_zaka}
        
        monthly_amounts = [zaka_map.get(code, 0) for code, name in months_list]
        
        report_data.append({
            'jumuiya': member.jumuiya.name if member.jumuiya else "No Jumuiya",
            'full_name': member.full_name,
            'months': monthly_amounts,
            'total': sum(zaka_map.values())
        })

    context = {
        'outstation': outstation,
        'report_data': report_data,
        'months_list': [m[1] for m in months_list],
        'selected_year': selected_year,
    }
    return render(request, 'zakao.html', context)

# --- SPECIAL CONTRIBUTIONS REPORT ---
def special_report(request, outstation_id):
    outstation = get_object_or_404(Outstation, id=outstation_id)
    selected_year = int(request.GET.get('year', date.today().year))
    
    # These are your model CHOICES
    types = ['ASSUMPTION', 'CHRISTMAS', 'PASAKA']
    
    # Optimization: Prefetch contributions for the year
    specials_qs = SpecialContribution.objects.filter(date_recorded__year=selected_year)
    members = Member.objects.filter(outstation=outstation).select_related('jumuiya')\
                    .prefetch_related(Prefetch('specialcontribution_set', queryset=specials_qs, to_attr='yearly_specials'))
    
    report_data = []
    for member in members:
        # Map: { 'CHRISTMAS': 500, 'PASAKA': 1000 }
        special_map = {s.contribution_type: s.amount for s in member.yearly_specials}
        row_amounts = [special_map.get(t, 0) for t in types]
        
        report_data.append({
            'jumuiya': member.jumuiya.name if member.jumuiya else "-",
            'name': member.full_name,
            'types': row_amounts,
            'total': sum(row_amounts)
        })

    return render(request, 'special_rpt.html', {
        'outstation': outstation,
        'report_data': report_data,
        'types': types,
        'year': selected_year
    })

# --- MAVUNO REPORT ---
def mavuno_report(request, outstation_id):
    outstation = get_object_or_404(Outstation, id=outstation_id)
    selected_year = int(request.GET.get('year', date.today().year))
    
    # List of produce types from your model
    produce_list = ['MAIZE', 'BEANS', 'WHEAT', 'MILLET', 'COW', 'GOAT', 'SHEEP', 'CHICKEN', 'MONEY']
    
    mavuno_qs = Mavuno.objects.filter(date_recorded__year=selected_year)
    members = Member.objects.filter(outstation=outstation).select_related('jumuiya')\
                    .prefetch_related(Prefetch('mavuno_set', queryset=mavuno_qs, to_attr='yearly_mavuno'))
    
    report_data = []
    for member in members:
        # Map: { 'MAIZE': 2, 'COW': 1 }
        mavuno_map = {m.produce_type: m.quantity for m in member.yearly_mavuno}
        row_quantities = [mavuno_map.get(p, 0) for p in produce_list]
        
        report_data.append({
            'jumuiya': member.jumuiya.name if member.jumuiya else "-",
            'name': member.full_name,
            'items': row_quantities,
        })

    return render(request, 'mavuno_report.html', {
        'outstation': outstation,
        'report_data': report_data,
        'produce_list': produce_list,
        'year': selected_year
    })