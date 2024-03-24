from django.urls import path, include
from core.views import index, product_list_view, category_list_view, category_product_list_view, vendor_list_view, vendor_detail_view, product_detail_view, tag_list, ajax_add_review, search_view, filter_product, checkout_view, add_to_cart, cart_view, delete_item_from_cart, update_from_cart, payment_completed_view, payment_failed_view

app_name = 'core'

urlpatterns = [
    # Define the URL pattern for the index view
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("products/<pid>/", product_detail_view, name="product-detail"),

    # Category

    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category-product-list"),

    # Vendor

    path("vendor/", vendor_list_view, name="vendor-list"),
    path("vendor/<str:vid>/", vendor_detail_view, name="vendor-detail"),

    # Tags

    path("products/tag/<slug:tag_slug>/", tag_list, name="tags"),

    # Add Reviews url

    path('ajax-add-review/<int:pid>/', ajax_add_review, name='ajax-add-review'),
    # path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),

    # Search
    path("search/", search_view, name="search"),

    # Filter products
    path("filter-products/", filter_product, name="filter-products"),

    # Add to Cart
    path("add-to-cart/", add_to_cart, name="add-to-cart"),
    path("cart/", cart_view, name="cart"),

    # Delete Items from Cart
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),

    # Update Items from Cart
    path("update-cart/", update_from_cart, name="update-cart"),


    # CheckOut
    path("checkout/", checkout_view, name="checkout"),

    # PayPal Url
    path('paypal/', include('paypal.standard.ipn.urls')),

    # Payment Succesful
    path("payment-completed/", payment_completed_view, name="payment-completed"),

    # Payment Succesful
    path("payment-failed/", payment_failed_view, name="payment-failed"),




]

