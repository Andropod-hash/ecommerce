from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, Wishlist, Address
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Q
from taggit.models import Tag
from core.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages

from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required


# Create your views here.

def index(request):

    # products = Product.objects.all().order_by("-id")
    products = Product.objects.filter(product_status="published", featured=True)

    context = {
        "products":products
    }

    return render(request, 'core/index.html', context)



def product_list_view(request):

    products = Product.objects.filter(product_status="published")



    context = {
        "products":products,
    }

    return render(request, 'core/product-list.html', context)

def category_list_view(request):

    categories = Category.objects.all()

    context = {
        "categories":categories
    }
    return render(request, 'core/category-list.html', context)

def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published", category=category)

    context = {
        "category":category,
        "products":products,
    }
    return render(request, 'core/category-product-list.html', context)


def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {
        "vendors":vendors
    }
    return render(request, "core/vendor-list.html", context)

def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published")
    context = {
        "vendor":vendor,
        "products":products,
    }
    return render(request, "core/vendor-detail.html", context)

def product_detail_view(request, pid):

    product = Product.objects.get(pid=pid)

    # Or you can use this code to get an object too , first import the get_objects_or_404

    # then you say product = get_objects_or_404(Product, pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)
    # This code retrieves the products that are in the same category with the product
                               # OR
    # products = Product.objects.filter(category=product.category).exclude(pid=pid)[:10]
    # This is to get the first 10 related posts

    # Getting All Reviews related to a product
    reviews = ProductReview.objects.filter(product=product).order_by("-date")

     # Getting All Average Reviews
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    # Products review form

    review_form = ProductReviewForm

    make_review = True
    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()
        if user_review_count > 0:
            make_review = False

    p_image = product.p_images.all()

    context = {
        "p":product,
        "p_image":p_image,
        "make_review":  make_review,
        "review_form":  review_form,
        "average_rating":average_rating,
        "reviews":reviews,
        "products":products,
    }
    return render(request, "core/product-detail.html", context)

def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-id")
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        "products":products,
        "tag":tag,
    }
    return render(request, "core/tag.html", context)


def ajax_add_review(request, pid):

    # Retrieve the product using the provided product ID (pid)
    product = Product.objects.get(pk=pid)

    # Get the currently logged-in user from the request
    user = request.user

    # Create a new ProductReview object and save it to the database
    review = ProductReview.objects.create(
        user = user,
        product = product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    # Calculate the average rating for the product's reviews
    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    return JsonResponse(
       {
            'bool': True,
            'context':context,
            'average_reviews' : average_reviews,
       }
    )

# def search_view(request):
#     # query = request.Get['q'] Or
#     query = request.GET.get('q')
#     products = Product.objects.filter(title__icontains=query, description__icontains=query).order_by("-date")

#     # We can use Startith when we want to search a product with first letters but Icontain will seacr base on the letters
#     # xample of Icontain, Imegine searching for Bitter Kola and we have Biter Lemon in the database, If we search "Bitter" Bitter Lemon will come out bkus we have Bitter in waht we are searhing

#     context = {
#         "products": products,
#         "query": query,
#     }

#     return render(request, "core/search.html", context)

def search_view(request):
    # query = request.Get['q'] Or
    query = request.GET.get("q")
    products = Product.objects.filter(Q(title__icontains=query)|Q(description__icontains=query)).order_by("-date")

    # We can use Startswith when we want to search a product with the first letters, but Icontains will search based on the letters.
    # Example of Icontains: Imagine searching for Bitter Kola, and we have Biter Lemon in the database. If we search "Bitter," Bitter Lemon will come out because we have "Bitter" in what we are searching.

    context = {
        "products": products,
        "query": query,
    }

    return render(request, "core/search.html", context)

def filter_product(request):
    categories = request.GET.getlist('category[]')
    vendors = request.GET.getlist('vendor[]')

    min_price = request.GET['min_price']
    max_price = request.GET['max_price']

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()

    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors) > 0:
        vendors = products.filter(vendor__id__in=vendors).distinct()

    # context = {
    #     "products": products
    # }


    data = render_to_string("core/async/product-list.html", {"products": products})

    return JsonResponse({"data": data})


def add_to_cart(request):
    # Initialize an empty dictionary to store product information for the current request
    cart_product = {}

    # Extract product information from the request's GET parameters and store it in the cart_product dictionary
    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
    }

    # Check if 'cart_data_obj' is already in the user's session
    if 'cart_data_obj' in request.session:

    # Check if the current product ID is already in the cart
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data

        else:
            # If the product is not in the cart, add it to the existing cart data
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data

    else:
        # If there is no cart data in the session, initialize it with the current product
        request.session['cart_data_obj'] = cart_product
    # Return a JSON response containing the updated cart data and the total number of items in the cart
    return JsonResponse({"data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})


def cart_view(request):
    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
           cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    else:
        messages.warning(request, "Your Cart Is Empty")
        return redirect("core:index")
        # return render(request, "core/cart.html",  {"cart_data":"", 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})



def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html",  {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})


def update_from_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html",  {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})

@login_required
def checkout_view(request):
    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,  # Fixing the typo here
        'amount': '1',
        'item_name': "Order-Item-No-4",
        'Invoice': "INV_NO-4 ",
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host, reverse("core:paypal-ipn")),
        'return_url': 'http://{}{}'.format(host, reverse("core:payment-completed")),
        'cancel_return': 'http://{}{}'.format(host, reverse("core:payment-failed")),
    }
    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)  # Matching the variable name

    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    return render(request, "core/checkout.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount, 'paypal_payment_button': paypal_payment_button})


def payment_completed_view(request):

    return render(request, 'core/payment-completed.html')

def payment_failed_view(request):

    return render(request, 'core/payment-failed.html')








