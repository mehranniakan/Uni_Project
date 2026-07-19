import uuid
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.core.signing import BadSignature, loads
from Account.models import User
from Clinic.models import Clinics
from Receptions.models import News


def index(request):
    secs = Clinics.objects.all().values_list("id", "name")
    users = User.objects
    news = News.objects

    top_docs = (
        users.filter(role="doctor", is_active=True, doctor__is_top=True)
        .select_related(
            "doctor",
            "doctor__clinic",
        )
        .prefetch_related(
            "doctor__services",
        )[:7]
    )

    pop_docs = (
        users.filter(role="doctor", is_active=True, doctor__is_popular=True)
        .select_related(
            "doctor",
            "doctor__clinic",
        )
        .prefetch_related(
            "doctor__services",
        )[:7]
    )

    news = news.all()[:7]
    return render(
        request,
        "index.html",
        {
            "items": secs,
            "top_docs": top_docs,
            "pop_docs": pop_docs,
            "news": news,
        },
    )


def docs(request):
    return render(request, "doctors_pub.html")


def news(request):
    obj = News.objects.all()
    page_obj = Paginator(obj, 12)
    page = request.GET.get("page")
    page_obj = page_obj.get_page(page)

    return render(
        request,
        "blog.html",
        {
            "page_obj": page_obj,
        },
    )


def single_news(request):

    if request.method == "GET" and request.GET.get("news_id"):
        try:
            real_uuid = loads(request.GET.get("news_id"))
            real_uuid = uuid.UUID(real_uuid)
        except BadSignature:
            return redirect("main")

        news = get_object_or_404(News, pk=real_uuid)

        return render(
            request,
            "single-blog.html",
            {
                "news": news,
            },
        )


def about_us(request):
    return render(request, "about-us.html")


def contact_us(request):
    return render(request, "contact-us.html")


def test(request):
    return render(request, "test.html")
