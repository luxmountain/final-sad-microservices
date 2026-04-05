from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Clothes
from .serializers import ClothesSerializer

class ClothesListCreate(APIView):
    def get(self, request):
        cat_id = request.query_params.get('category_id')
        
        if cat_id:
            clothes = Clothes.objects.filter(category_id=cat_id)
        else:
            clothes = Clothes.objects.all()
            
        serializer = ClothesSerializer(clothes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClothesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClothesDetail(APIView):
    """GET / PUT / DELETE cho 1 món quần áo theo ID"""

    def get_object(self, pk):
        try:
            return Clothes.objects.get(pk=pk)
        except Clothes.DoesNotExist:
            return None

    def get(self, request, pk):
        clothes = self.get_object(pk)
        if not clothes:
            return Response({"error": "Sản phẩm không tồn tại!"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClothesSerializer(clothes).data)

    def put(self, request, pk):
        clothes = self.get_object(pk)
        if not clothes:
            return Response({"error": "Sản phẩm không tồn tại!"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClothesSerializer(clothes, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        clothes = self.get_object(pk)
        if not clothes:
            return Response({"error": "Sản phẩm không tồn tại!"}, status=status.HTTP_404_NOT_FOUND)
        clothes.delete()
        return Response({"message": f"Đã xóa sản phẩm #{pk} khỏi kho!"}, status=status.HTTP_200_OK)