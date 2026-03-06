
from django.shortcuts import render,redirect, get_object_or_404
from django.db.models import Q
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
from django.core.mail import send_mail
from django.conf import settings 
from .decorators import superuser_or_usertype
from .models import *
from users.models import CustomUser, Catechist

from django.contrib import messages
# views.py


def catechist_list(request):
    # Ensure only the Priest (user_type 1) can see this list
    if request.user.user_type != '1':
        return redirect('Dashbd')
    
    # Get all profiles for user type '3'
    catechists = Catechist.objects.select_related('admin', 'outstation').all()
    return render(request, 'catechist_list.html', {'catechists': catechists})
def assign_outstation(request, catechist_id):
    if request.user.user_type != '1':
        return redirect('Dashbd')

    catechist = get_object_or_404(Catechist, id=catechist_id)
    outstations = Outstation.objects.all()

    if request.method == "POST":
        # Update User Model Fields
        user = catechist.admin
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        # Ensure 'phone' exists in your CustomUser model
        if hasattr(user, 'phone'):
            user.phone = request.POST.get('phone')
        user.save()

        # Update Catechist Profile Fields
        catechist.outstation_id = request.POST.get('outstation')
        catechist.gender = request.POST.get('gender')
        catechist.address = request.POST.get('address')
        catechist.save()

        return redirect('catechist_list')

    return render(request, 'update.html', {'catechist': catechist, 'outstations': outstations})


@login_required
def mon_report(request):
    catechist = request.user.catechist
    outstation = catechist.outstation
    zaka = Zaka.objects.filter(member__outstation=outstation)

    context = {
        'outstation': outstation,
        'zaka': zaka,
    }
    return render(request, 'aka.html', context)


@login_required
def zak_report(request):
    catechist = request.user.catechist
    outstation = catechist.outstation
    special = SpecialContribution.objects.filter(member__outstation=outstation)

    context = {
        'outstation': outstation,
        'special': special,
    }
    return render(request, 'cial_report.html', context)


@login_required
def mavreport(request):
    catechist = request.user.catechist
    outstation = catechist.outstation
    mavuno = Mavuno.objects.filter(member__outstation=outstation)

    context = {
        'outstation': outstation,
        'mavuno': mavuno,
    }
    return render(request, 'vuno_report.html', context)


@login_required
def sadreport(request):
    catechist = request.user.catechist
    outstation = catechist.outstation
    sadaka = Sadaka.objects.filter(outstation=outstation)

    context = {
        'outstation': outstation,
        'sadaka': sadaka,
    }
    return render(request, 'sada_report.html', context)


@login_required
def jumu_report(request):
    catechist = request.user.catechist
    outstation = catechist.outstation
    jumuiya = JumuiyaContribution.objects.filter(jumuiya__outstation=outstation)

    context = {
        'outstation': outstation,
        'jumuiya': jumuiya,
    }
    return render(request, 'jumureport.html', context)
@login_required
@superuser_or_usertype(allowed_types=[ '3'])
def catechist_dashboard(request):
    # Only catechists can access
    if request.user.user_type != '3':
        return redirect('Dashbd')  # redirect non-catechists

    catechist_profile = get_object_or_404(Catechist, admin=request.user)

    # Only members in their assigned outstation
    members = Member.objects.filter(outstation=catechist_profile.outstation)

    context = {
        'members': members,
        'outstation': catechist_profile.outstation,
    }
    return render(request, 'cate_dashbd.html', context)
def home (request):
    return render(request, 'home.html')
# Create your views here.
def  about(request):
    return render(request, 'about.html')
  
from users.utils import send_background_email
def Contact(request): 
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        context = {
            'name': name,
            'email': email,
            'phone': phone,
            'message': message
        }

        # Send to yourself in background
        send_background_email(
            subject="New Contact Form Message",
            recipient_email="kevinmalasa2000@gmail.com",
            template_name='emails/contact_notification.html',
            context=context
        )

        return render(request, "contact.html", {"success": True, "title": title})
    return render(request, "contact.html", {"title": title})
# def CatechistDashboard(request):
#     return render(request, 'catechist_dashboard.html')
@superuser_or_usertype(allowed_types=['1', '2'])

def StaffDashboard(request):
    selected_year = int(request.GET.get('year', date.today().year))
    outstations = Outstation.objects.all()
    
    report_data = []
    # Initialize Parish (Grand) Totals
    parish_totals = {
        'zaka': 0,
        'special': 0,
        'jumuiya': 0,
        'mavuno_cash': 0,
    }

    for station in outstations:
        # 1. Zaka per Station
        zaka_total = Zaka.objects.filter(
            member__outstation=station, 
            year=selected_year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 2. Special Contribution per Station
        special_total = SpecialContribution.objects.filter(
            member__outstation=station, 
            date_recorded__year=selected_year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 3. Jumuiya Contributions per Station
        jumuiya_total = JumuiyaContribution.objects.filter(
            jumuiya__outstation=station, 
            year=selected_year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 4. Mavuno (Money type) per Station
        mavuno_cash = Mavuno.objects.filter(
            member__outstation=station, 
            produce_type='MONEY', 
            date_recorded__year=selected_year
        ).aggregate(total=Sum('quantity'))['total'] or 0

        station_sum = zaka_total + special_total + jumuiya_total + mavuno_cash

        # Append to report list
        report_data.append({
            'name': station.name,
            'zaka': zaka_total,
            'special': special_total,
            'jumuiya': jumuiya_total,
            'mavuno_cash': mavuno_cash,
            'total': station_sum
        })

        # Add to Grand Totals
        parish_totals['zaka'] += zaka_total
        parish_totals['special'] += special_total
        parish_totals['jumuiya'] += jumuiya_total
        parish_totals['mavuno_cash'] += mavuno_cash

    parish_grand_total = sum(parish_totals.values())

    context = {
        'report_data': report_data,
        'parish_totals': parish_totals,
        'parish_grand_total': parish_grand_total,
        'year': selected_year,
    }
    return render(request, 'staff_dashboard.html', context)
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
@superuser_or_usertype(allowed_types=['1'])
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
        {'url': '/static/images/event4.jpg', 'title': 'Community Outreach', 'alt': 'Outreach'}, 
        {'url': '/static/images/event5.jpg', 'title': 'Annual Picnic', 'alt': 'Picnic'},   
    ]
    return render(request, 'gallary.html', {'photos': photos})


def jumuiya_contribution(request):
    query = request.GET.get('q', '')
    
    # Filter Jumuiyas based on search (searches Jumuiya name or Outstation name)
    jumuiyas = Jumuiya.objects.all()
    if query:
        jumuiyas = jumuiyas.filter(
            Q(name__icontains=query) | 
            Q(outstation__name__icontains=query)
        )

    # Filter Contribution History
    contributions = JumuiyaContribution.objects.order_by('-date_recorded')
    if query:
        contributions = contributions.filter(
            Q(jumuiya__name__icontains=query) | 
            Q(jumuiya__outstation__name__icontains=query) |
            Q(year__icontains=query)
        )

    if request.method == "POST":
        jumuiya_id = request.POST.get('jumuiya')
        year = request.POST.get('year')
        amount = request.POST.get('amount')

        if not jumuiya_id:
            messages.error(request, "Please select a Jumuiya.")
            return redirect('jumuiya_contribution')

        # Logic for amount validation
        try:
            if float(amount) < 20000:
                messages.error(request, "Amount must be 20,000 or above.")
                return redirect('jumuiya_contribution')
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect('jumuiya_contribution')

        # Prevent duplicate year entry
        if JumuiyaContribution.objects.filter(jumuiya_id=jumuiya_id, year=year).exists():
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
        'contributions': contributions,
        'query': query # Pass query back to template to keep search box filled
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


def Admin(request):
    return render(request, 'adminstration.html')
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
def station_INT(request):
    return render(request, 'stat.html')


def parish_mavuno_report(request):
    selected_year = int(request.GET.get('year', date.today().year))

    produce_cols = ['MAIZE', 'BEANS', 'WHEAT', 'CHICKEN', 'SHEEP', 'MILLET', 'COW']

    outstations = Outstation.objects.all()
    report_data = []

    # Parish grand totals
    grand_total_pledged = 0
    grand_total_actual = 0
    grand_total_produce = {p: 0 for p in produce_cols}

    for station in outstations:
        station_groups = []
        subtotal_pledged = 0
        subtotal_actual = 0
        subtotal_produce = {p: 0 for p in produce_cols}

        jumuiyas = Jumuiya.objects.filter(outstation=station)

        for j in jumuiyas:
            produce_data = {}
            for p_type in produce_cols:
                qty = Mavuno.objects.filter(
                    member__jumuiya=j,
                    produce_type=p_type,
                    date_recorded__year=selected_year
                ).aggregate(total=Sum('quantity'))['total'] or 0
                produce_data[p_type] = qty
                subtotal_produce[p_type] += qty
                grand_total_produce[p_type] += qty

            # CASH (MONEY)
            actual = Mavuno.objects.filter(
                member__jumuiya=j,
                produce_type='MONEY',
                date_recorded__year=selected_year
            ).aggregate(total=Sum('quantity'))['total'] or 0

            # TODO: if you have pledged amount, replace 0
            pledged = 0

            subtotal_pledged += pledged
            subtotal_actual += actual
            grand_total_pledged += pledged
            grand_total_actual += actual

            station_groups.append({
                'name': j.name,
                'pledged': pledged,
                'actual': actual,
                'produce': produce_data
            })

        report_data.append({
            'station_name': station.name,
            'jumuiyas': station_groups,
            'subtotal_pledged': subtotal_pledged,
            'subtotal_actual': subtotal_actual,
            'subtotal_produce': subtotal_produce
        })

    return render(request, 'parish_report.html', {
        'report_data': report_data,
        'year': selected_year,
        'grand_total_pledged': grand_total_pledged,
        'grand_total_actual': grand_total_actual,
        'grand_total_produce': grand_total_produce
    })
def parish_special_report(request):
    selected_year = int(request.GET.get('year', date.today().year))

    contribution_types = ['ASSUMPTION', 'CHRISTMAS', 'PASAKA']

    outstations = Outstation.objects.all()
    report_data = []
    grand_total = 0

    for station in outstations:
        station_groups = []
        station_total = 0

        jumuiyas = Jumuiya.objects.filter(outstation=station)

        for j in jumuiyas:
            type_totals = {}
            jumuiya_total = 0

            for ctype in contribution_types:
                total = SpecialContribution.objects.filter(
                    member__jumuiya=j,
                    contribution_type=ctype,
                    date_recorded__year=selected_year
                ).aggregate(sum=Sum('amount'))['sum'] or 0

                type_totals[ctype] = total
                jumuiya_total += total

            station_groups.append({
                'name': j.name,
                'types': type_totals,
                'total': jumuiya_total
            })

            station_total += jumuiya_total

        report_data.append({
            'station_name': station.name,
            'jumuiyas': station_groups,
            'station_total': station_total
        })

        grand_total += station_total

    return render(request, 'parish_special_report.html', {
        'report_data': report_data,
        'year': selected_year,
        'grand_total': grand_total
    })


def parish_zaka_report(request):
    selected_year = int(request.GET.get('year', date.today().year))

    outstations = Outstation.objects.all()
    report_data = []
    grand_total = 0

    for station in outstations:
        station_groups = []
        station_total = 0

        jumuiyas = Jumuiya.objects.filter(outstation=station)

        for j in jumuiyas:
            total_zaka = Zaka.objects.filter(
                member__jumuiya=j,
                year=selected_year
            ).aggregate(sum=Sum('amount'))['sum'] or 0

            station_groups.append({
                'name': j.name,
                'total': total_zaka
            })

            station_total += total_zaka

        report_data.append({
            'station_name': station.name,
            'jumuiyas': station_groups,
            'station_total': station_total
        })

        grand_total += station_total

    return render(request, 'parish_zaka_report.html', {
        'report_data': report_data,
        'year': selected_year,
        'grand_total': grand_total
    })