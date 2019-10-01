"""View module for handling requests about park areas"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from kennywoodapi.models import ParkArea, Attraction, Itinerary, Customer
from .attraction import AttractionSerializer


class ItineraryItemSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for park areas

    Arguments:
        serializers
    """
    class Meta:
        model = Itinerary
        url = serializers.HyperlinkedIdentityField(
            view_name='itineraryitem',
            lookup_field='id'
        )
        fields = ('id', 'url', 'starttime', 'attraction')
        depth = 2


class ItineraryItems(ViewSet):
    """Itinerary Items for Kennywood Amusement Park"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized Itinerary instance
        """
        newitem = Itinerary()
        newitem.starttime = request.data["starttime"]
        newitem.customer = Customer.objects.get(user=request.auth.user)
        newitem.attraction = Attraction.objects.get(pk=request.data["ride_id"])
        newitem.save()

        serializer = ItineraryItemSerializer(newitem, context={'request': request})

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single itinerary item

        Returns:
            Response -- JSON serialized itinerary instance
        """
        try:
            itinerary_item = Itinerary.objects.get(pk=pk)
            serializer = ItineraryItemSerializer(itinerary_item, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for an itinerary item

        Returns:
            Response -- Empty body with 204 status code
        """
        item = Itinerary.objects.get(pk=pk)
        item.name = request.data["name"]
        item.theme = request.data["theme"]
        item.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single itinerary item are

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            item = Itinerary.objects.get(pk=pk)
            item.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Itinerary.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to list itinerary items for authenticated customer

        Returns:
            Response -- JSON serialized list of park areas
        """
        customer = Customer.objects.get(user=request.auth.user)
        items = Itinerary.objects.filter(customer=customer)

        serializer = ItineraryItemSerializer(
            items, many=True, context={'request': request})
        return Response(serializer.data)
