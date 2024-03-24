from core.models import Product, Category, Vendor, Address
from django.db.models import Min, Max
from userauths.models import User
def default(request):
    # if request.user.is_authenticated:
    #    address = Address.objects.get(user=request.user)
    # else:
    #     address=None

    categories = Category.objects.all()


    vendors = Vendor.objects.all()
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))


    return {
        'categories': categories,
        # 'address':address,
        'vendors': vendors,
        "min_max_price": min_max_price
    }


