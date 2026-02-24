from django.shortcuts import render, redirect
from .forms import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date


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
            messages.success("Registered Member succefully")
            return redirect('register_member')  # You can also redirect to a success page or the member list page after saving
            # redirect to members page or success message
    context = {'form': form}
    return render(request, 'register_member.html', context)

def jumuiya(request):
    if request.method == 'POST':
        form = JumuiyaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register_member')
    else:
        form = JumuiyaForm()   

    context = {
        'form': form
    }
    return render(request, 'jumuiya.html', context)
def out_station(request):
    if request.method == 'POST':
        form = OutstationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success('Recorded station succeffully')
            return redirect('Dashbd')
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

    members = Member.objects.all()

    # # SEARCH FILTER
    # outstation = request.GET.get('outstation')
    # jumuiya = request.GET.get('jumuiya')

    # if outstation:
    #     members = members.filter(outstation__icontains=outstation)

    # if jumuiya:
    #     members = members.filter(jumuiya__icontains=jumuiya)

    # FORM SAVE
    if request.method == 'POST':
        form = ZakaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "zaka recorded successfully!")
            return redirect('zaka')
    else:
        form = ZakaForm()

    context = {
        'form': form,
        'members': members
    }

    return render(request, 'zaka.html', context)
@login_required(login_url='Login')
def mavuno(request):
    if request.method == 'POST':
        form = MavunoForm(request.POST)
        if form.is_valid():   
            form.save()
            messages.success(request, "Mavuno recorded successfully!")
            return redirect('mavuno')
            
    else:
        form = MavunoForm()   

    context = {
        'form': form
        
    }
    return render(request, 'mavuno.html', context)
@login_required(login_url='Login')
def Special(request):
    if request.method == 'POST':
        form = SpecialForm(request.POST)
        if form.is_valid():   
            form.save()
            messages.success(request, "Reecorded successfully!")
            return redirect('Dashbd')
    else:
        form = SpecialForm()   

    context = {
        'form': form
    }
    return render(request, 'special.html', context)
@login_required(login_url='Login')
def Dashbd(request):
    outstations = Outstation.objects.all()
    outstation_data = []

    current_year = date.today().year

    for outstation in outstations:
        # Sadaka totals
        sadaka_weekly = Sadaka.objects.filter(outstation=outstation).order_by('-date_recorded')[:5]  # last 5 weeks
        sadaka_yearly = Sadaka.objects.filter(
            outstation=outstation, 
            date_recorded__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Mavuno totals per produce type
        mavuno_totals = {}
        for produce in ['MAIZE', 'BEANS', 'WHEAT']:
            total = Mavuno.objects.filter(
                member__outstation=outstation,
                produce_type=produce,
                date_recorded__year=current_year
            ).aggregate(total=Sum('quantity'))['total'] or 0
            mavuno_totals[produce] = total

        # Special contributions totals
        special_totals = {}
        for contrib in ['NOEL', 'CHRISTMAS', 'PASAKA']:
            total = SpecialContribution.objects.filter(
                member__outstation=outstation,
                contribution_type=contrib,
                date_recorded__year=current_year
            ).aggregate(total=Sum('amount'))['total'] or 0
            special_totals[contrib] = total

        # Zaka totals per year
        zaka_totals = {}
        zaka_records = Zaka.objects.filter(
            member__outstation=outstation, 
            date_recorded__year=current_year
        )
        for z in zaka_records:
            year = z.date_recorded.year
            zaka_totals[year] = zaka_totals.get(year, 0) + z.amount

        outstation_data.append({
            'outstation': outstation,
            'sadaka_weekly': sadaka_weekly,
            'sadaka_yearly': sadaka_yearly,
            'mavuno_totals': mavuno_totals,
            'special_totals': special_totals,
            'zaka_totals': zaka_totals,
        })

    context = {
        'outstation_data': outstation_data,
        'now': date.today(),  # for templates to show current year
    }

    return render(request, 'dash.html', context)



@login_required(login_url='Login')
def outstation(request, pk):
    outstation = get_object_or_404(Outstation, id=pk)
    members = Member.objects.filter(outstation=outstation)

    member_data = []

    for m in members:
        # Zaka: group by year
        zaka_qs = Zaka.objects.filter(member=m).order_by('date_recorded')
        zaka = {'A': [], 'B': [], 'C': []}
        for z in zaka_qs:
            zaka[z.year].append({
                'amount': z.amount,
                'year': z.year,
                'date': z.date_recorded,
            })

        # Special Contributions: group by type
        special_qs = SpecialContribution.objects.filter(member=m).order_by('date_recorded')
        special = {'NOEL': [], 'CHRISTMAS': [], 'PASAKA': []}
        for s in special_qs:
            special[s.contribution_type].append({
                'amount': s.amount,
                'date': s.date_recorded,
                'year': s.date_recorded.year,
            })

        # Mavuno: group by produce type
        mavuno_qs = Mavuno.objects.filter(member=m).order_by('date_recorded')
        mavuno = {'MAIZE': [], 'BEANS': [], 'WHEAT': []}
        for p in mavuno_qs:
            mavuno[p.produce_type].append({
                'quantity': p.quantity,
                'date': p.date_recorded,
                'year': p.date_recorded.year,
            })

        member_data.append({
            'member': m,
            'zaka': zaka,
            'special': special,
            'mavuno': mavuno,
        })

    context = {
        'outstation_name': outstation.name,
        'member_data': member_data,
        'now': None,
    }

    return render(request, 'detail.html', context)
@login_required(login_url='Login')
def sadaka(request):
    if request.method == 'POST':
        form = SadakaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sadaka recorded successfully!")
            return redirect('sadaka')
    else:
        form = SadakaForm()
    return render(request, 'sdk.html', {'form': form})