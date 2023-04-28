from django.views import generic

from product.models import *
from django.shortcuts import render
from django.http import JsonResponse,Http404
from django.db.models import Q
from django.middleware.csrf import get_token
import json


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
class ProductList(generic.ListView):
    model=Product
    template_name="products/list.html"
    context_object_name='products'
    paginate_by= 3
    paginate_orphans= 1
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["variant_price"]=ProductVariantPrice.objects.all()
        context["product_variant"]=ProductVariant.objects.values('variant','variant_title').distinct()
        return context
    def get_queryset(self):
        queryset=super().get_queryset()
        title=self.request.GET.get('title')
        variant=self.request.GET.get('variant')
        price_from=self.request.GET.get('price_from')
        price_to=self.request.GET.get('price_to')
        date=self.request.GET.get('date',None)
        
        if title:
            queryset=queryset.filter(title__icontains=title)
        if variant:
            queryset =queryset.filter(Q(productvariantprice__product_variant_one__variant_title=variant)| Q(productvariantprice__product_variant_two__variant_title=variant)| Q(productvariantprice__product_variant_three__variant_title=variant)) 
        if price_from and price_to:
            queryset=queryset.filter(productvariantprice__price__gte=price_from,productvariantprice__price__lte=price_to)      
        if date:
            queryset=queryset.filter(created_at__icontains=date)    
        return queryset
    def paginate_queryset(self, queryset, page_size) :

        try:
          
           return super(ProductList,self).paginate_queryset(queryset, page_size)
        except Http404:
           self.kwargs['page'] = 1
           return super(ProductList,self).paginate_queryset(queryset,page_size)
    
    
        
class GetData(generic.View):
     def get(self,request):
        v=ProductVariant.objects.all()
        
        return JsonResponse({"success":True})    
    
class CsrfToken(generic.View):
    def get(self,request,*args, **kwargs):
        return JsonResponse({"csrf":get_token(request)})


class postProduct(generic.View):
    def post(self,request):
        data=json.loads(request.body)
        print(data)
        product=data['product']
        create_product=Product.objects.create(title=product['name'],sku=product['sku'],description=product['description'])
        product_id=create_product.id
        print(product_id)
        
        variant=data['variant']
        variantPrice=data['variantprice']
        var_price=data['price']
        stock=data['stock']
            
        for var in variant:
            for i in var['tags']:
               
                create_productVariant=ProductVariant.objects.create(variant_title=i,variant_id=var['option'],product_id=product_id)
                pVariant_id=create_productVariant.id
               
                  
                       
                        
                        
                        
          
            
        VarPriceData=[]
        for price in variantPrice:
            arr=price['title'].split("/")
            proV=ProductVariant.objects.filter(variant_title=arr[0],product_id=product_id).values("id").distinct()
            proV1=ProductVariant.objects.filter(variant_title=arr[1],product_id=product_id).values("id").distinct()
            proV2=ProductVariant.objects.filter(variant_title=arr[2],product_id=product_id).values("id").distinct()
            priceStock=[{"price":price['price'],"stock":price['stock']}]
            print(price)
            for p,p1,p2 in zip(proV,proV1,proV2):
                
               
                varPrice={
                    "one":int(p['id']),
                    "two":int(p1['id']),
                    "three":int(p2['id']),
                   
                    
                }
                VarPriceData.append(varPrice)
            
                # 
        for pri,st,vpd in zip(var_price,stock,VarPriceData):
            create_productVariantPrice=ProductVariantPrice.objects.create(product_variant_one_id= int(vpd["one"]),product_variant_two_id=int(vpd["two"]) ,product_variant_three_id= int(vpd["three"]),price=int(pri),stock=int(st),product_id=product_id)
            
            
        print(variant)
        print(variantPrice)
        return JsonResponse({"success":True})        