from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Product, Cart, CartItem, Order, OrderItem, Category
from .serializers import CartItemSerializer, ProductSerializer, OrderItemSerializer, CategorySerializer,OrderSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer

# Просмотр для поиска продуктов
class SearchProducts(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'])
    def search_product(self, request):
        # Получаем идентификатор продукта из запроса
        pk = self.request.query_params.get('pk')
        try:
            # Пытаемся получить продукт по идентификатору
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
             # Если продукт не найден, возвращаем сообщение об ошибке
            return Response({'message': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)
        
# Работа с продуктами
class ProductsViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Действие для поиска продуктов по категории
    @action(detail=False, methods=['post'])
    def search_by_category(self, request):
        category_name = request.data.get('cat')
        category = Category.objects.filter(cat=category_name).first()
        
        if not category:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        products = Product.objects.filter(cat=category)
        serializer = ProductSerializer(products, many=True)
        
        return Response(serializer.data)
    
# Работа с корзиной
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartItemSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

# Действие для получения содержимого корзины
    @action(detail=False, methods=['get'])
    def get_cart(self, request):

        # Получаем пользователя
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)

        serializer = CartItemSerializer(cart.cartitem_set.all(), many=True) 
        return Response(serializer.data)

# Добавление продукта в корзину
    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):

        # Получаем текущего пользователя
        user = request.user
        product = get_object_or_404(Product, pk=pk)
        cart, created = Cart.objects.get_or_create(user=user)

        #Если продукт есть в корзине, то увел. кол-во на 1
        if product in cart.items.all():
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity += 1
            cart_item.save()
        else:
            # Иначе создаёт новый товар
            cart_item = CartItem.objects.create(cart=cart, product=product)

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Логика обновления количества позиции в корзине
    @action(detail=True, methods=['put'])
    def update_cart_item(self, request, pk=None):

        # Получаем текущего пользователя
        user = request.user

        # Получаем корзину пользователя
        cart = Cart.objects.get(user=user)

        # Получаем объект CartItem по его primary key (pk) и связанной корзине
        cart_item = get_object_or_404(CartItem, pk=pk, cart=cart)

        # Получаем новое количество товара из запроса
        quantity = request.data.get('quantity')

        # Проверяем, было ли передано новое количество
        if quantity:
            # Обновляем количество товара в корзине
            cart_item.quantity = quantity
            cart_item.save() # Сохраняем обновленное количество в базе данных

        # Сериализуем обновленный объект CartItem для возврата клиенту
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def remove_from_cart(self, request, pk=None):
        # Получаем текущего пользователя
        user = request.user
        # Получаем корзину пользователя
        cart = Cart.objects.get(user=user)
        try:
            # Получаем объект CartItem для удаления по его primary key (pk) и связанной корзине
            cart_item = get_object_or_404(CartItem, pk=pk, cart=cart)
            cart_item.delete() # Удаляем позицию из корзины

            # Возвращаем сообщение об успешном удалении
            return Response({'message': 'Предмет успешно удалён'}, status=status.HTTP_204_NO_CONTENT) 
        except  Http404:
             # Возвращаем сообщение о неудачном удалении
             return Response({'message': 'Такого продукта нет в корзине'}, status=status.HTTP_404_NOT_FOUND)

# Работа с заказми
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderItemSerializer

    # Создание заказа на основе содержимого корзины
    @action(detail=False, methods=['post'])
    def create_order(self, request):

        # Получаем текущего пользователя
        user = request.user

        # Получаем корзину пользователя
        cart = Cart.objects.get(user=user)

        # Получаем все позиции корзины
        cart_items = cart.cartitem_set.all()

        if cart_items: # Если в корзине есть позиции

            # Вычисляем общую стоимость заказа на основе содержимого корзины
            total_price = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)

            # Создаем новый заказ для пользователя с указанной общей стоимостью
            order = Order.objects.create(user=user, total_price=total_price)

            # Создаем записи OrderItem для каждой позиции из корзины пользователя
            for cart_item in cart_items:
                OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)

            # Очищаем корзину пользователя после успешного создания заказа
            cart.items.clear()

            # Сериализуем созданный заказ
            serializer = OrderSerializer(order)

            # Возвращаем созданный заказ с кодом 201
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:

            # Возвращаем ошибку, если корзина пуста
            return Response({'message': 'Невозможно создать пустой заказ. Корзина пуста.'}, status=status.HTTP_400_BAD_REQUEST)