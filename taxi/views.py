from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Driver, Car, Manufacturer
from .forms import (
    DriverCreationForm,
    DriverLicenseUpdateForm,
    CarForm,
    DriversSearchForm,
    ManufacturerSearchForm,
    CarsSearchForm
)


@login_required
def index(request):
    """View function for the home page of the site."""

    num_drivers = Driver.objects.count()
    num_cars = Car.objects.count()
    num_manufacturers = Manufacturer.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_drivers": num_drivers,
        "num_cars": num_cars,
        "num_manufacturers": num_manufacturers,
        "num_visits": num_visits + 1,
    }

    return render(request, "taxi/index.html", context=context)


class ManufacturerListView(LoginRequiredMixin, generic.ListView):
    model = Manufacturer
    context_object_name = "manufacturer_list"
    template_name = "taxi/manufacturer_list.html"
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ManufacturerListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = ManufacturerSearchForm(
            initial={"name": name}
        )
        return context

    def get_queryset(self):
        queryset = Manufacturer.objects.get_queryset().order_by("id")
        name = self.request.GET.get("name")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset


class ManufacturerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Manufacturer
    success_url = reverse_lazy("taxi:manufacturer-list")


class CarListView(LoginRequiredMixin, generic.ListView):
    model = Car
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CarListView, self).get_context_data(**kwargs)
        model = self.request.GET.get("model", "")
        context["search_form"] = CarsSearchForm(
            initial={"model": model}
        )
        return context

    def get_queryset(self):
        queryset = Car.objects.select_related("manufacturer").order_by("id")
        model = self.request.GET.get("model")
        if model:
            return queryset.filter(model__icontains=model)
        return queryset


class CarDetailView(LoginRequiredMixin, generic.DetailView):
    model = Car


class CarCreateView(LoginRequiredMixin, generic.CreateView):
    model = Car
    form_class = CarForm
    success_url = reverse_lazy("taxi:car-list")


class CarUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Car
    form_class = CarForm
    success_url = reverse_lazy("taxi:car-list")


class CarDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Car
    success_url = reverse_lazy("taxi:car-list")


class DriverListView(LoginRequiredMixin, generic.ListView):
    model = Driver
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DriverListView, self).get_context_data(**kwargs)
        username = self.request.GET.get("username", "")
        context["search_form"] = DriversSearchForm(
            initial={"username": username},
        )
        return context

    def get_queryset(self):
        queryset = Driver.objects.all().order_by("id")
        username = self.request.GET.get("username")
        if username:
            return queryset.filter(username__icontains=username)
        return queryset


class DriverDetailView(LoginRequiredMixin, generic.DetailView):
    model = Driver
    queryset = Driver.objects.all().prefetch_related("cars__manufacturer")


class DriverCreateView(LoginRequiredMixin, generic.CreateView):
    model = Driver
    form_class = DriverCreationForm


class DriverLicenseUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Driver
    form_class = DriverLicenseUpdateForm
    success_url = reverse_lazy("taxi:driver-list")


class DriverDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Driver
    success_url = reverse_lazy("")


@login_required
def toggle_assign_to_car(request, pk):
    driver = Driver.objects.get(id=request.user.id)
    if (
        get_object_or_404(Car, id=pk) in driver.cars.all()
    ):  # probably could check if car exists; should be good now
        driver.cars.remove(pk)
    else:
        driver.cars.add(pk)
    return HttpResponseRedirect(reverse_lazy("taxi:car-detail", args=[pk]))
