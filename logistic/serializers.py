from rest_framework import serializers

from logistic.models import Product, StockProduct, Stock


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['address', 'positions']
    # настройте сериализатор для склада

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        # заполняем связанную таблицу
        for position in positions:
            position['stock'] = stock
            product_id = position['product'].id
            stock_id = position['stock'].id
            StockProduct.objects.update_or_create(product=product_id, stock=stock_id, defaults=position)

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        # обновляем связанную таблицу
        old_positions = StockProduct.objects.filter(stock=stock.id)
        old_positions.delete()
        for position in positions:
            position['stock'] = stock
            product_id = position['product'].id
            stock_id = position['stock'].id
            StockProduct.objects.update_or_create(product=product_id, stock=stock_id, defaults=position)

        return stock
