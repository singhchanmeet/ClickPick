from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from . models import ActiveOrders, PastOrders, ActivePrintOuts, PastPrintOuts, Items, TempFileStorage
from . serializers import ActiveOrdersSerializer, PastOrdersSerializer, ActivePrintoutsSerializer, PastPrintoutsSerializer, ItemsSerializer

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import os
from pathlib import Path

from math import ceil

from .calculate_cost.pdf import check_black_content
from .calculate_cost.word import word_to_images
from .calculate_cost.word import images_to_pdfs
from .generate_firstpage import firstpage


import os  # Import the os module for operating system functions


from django.shortcuts import redirect






import requests

def convert_docx_to_pdf(file_path):
    url = "http://panel.mait.ac.in:8009/api/convert/"

    try:
        with open(file_path, 'rb') as file:
            files = {'docx_file': file}
            response = requests.post(url, files=files)
            if response.status_code == 200:
                # Save the returned PDF file
                # with open("converted.pdf", 'wb') as pdf_file:
                #     pdf_file.write(response.content)
                return response.content
            else:
                print("Error occurred:", response.text)
    except Exception as e:
        print("Exception occurred:", str(e))










# To get all Items
class GetItemList(APIView):
    
    permission_classes = (IsAuthenticated, )

    def get(self, request):

        all_items = Items.objects.all()
        serializer = ItemsSerializer(all_items, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)




# To get all active orders of the logged in user
class GetActiveOrders(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        
        user = request.user
        all_orders = ActiveOrders.objects.filter(user=user)
        serializer = ActiveOrdersSerializer(all_orders, many=True)
        orders_data = []

        for order in serializer.data:
            item = Items.objects.get(pk=order['item'])
            order['item_name'] = item.item
            order['item_display_image'] = item.display_image.url
            orders_data.append(order)

        return Response(orders_data, status=status.HTTP_200_OK)


# To get all past orders of the logged in user
class GetPastOrders(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        
        user = request.user
        all_orders = PastOrders.objects.filter(user=user)
        serializer = PastOrdersSerializer(all_orders, many=True)
        orders_data = []

        for order in serializer.data:
            item = Items.objects.get(pk=order['item'])
            order['item_name'] = item.item
            order['item_display_image'] = item.display_image.url
            orders_data.append(order)

        return Response(orders_data, status=status.HTTP_200_OK)

# To get all active printouts of the logged in user
class GetActivePrintouts(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        
        all_orders = ActivePrintOuts.objects.filter(user=request.user)
        serializer = ActivePrintoutsSerializer(all_orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

# To get all past printouts of the logged in user
class GetPastPrintouts(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        
        all_orders = PastPrintOuts.objects.filter(user=request.user)
        serializer = PastPrintoutsSerializer(all_orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)







# To create a single order or multiple orders at once
class CreateOrder(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request):

        # key value pair is coming
        # key is named 'orders', value is a list of orders
        # {
        #   'orders': [ {'item' : RING_FILE, 'quantity': 2, 'cost': 40}, {'item' : PEN, 'quantity': 3, 'cost': 30}, ]
        # } 

        orders = request.data.get('orders')

        for order in orders:
            data = {
                'user' : request.user.pk,
                'item' : Items.objects.filter(item=order['item']).first().pk,
                'quantity' : int(order['quantity']),
                'cost' : float(order['cost']),
                'custom_message' : order['custom_message'],
            }

            serializer = ActiveOrdersSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
            else:
                return Response({'message': 'Order Creation Failed'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'message': 'Orders Created Successfully'}, status=status.HTTP_200_OK)

# To create a single printout order    
'''class CreatePrintout(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request):
        
        try:

            printouts_data = request.data.getlist('printouts', [])  # Assuming 'printouts' is the key for the list of printouts

            print("\n")
            print(type(printouts_data))

            for printout_data in printouts_data:
                print(type(printout_data))
                # file = printout_data.get('file')
                data = {
                    'user': request.user.pk,
                    'coloured_pages': printout_data.get('coloured_pages'),
                    'black_and_white_pages': printout_data.get('black_and_white_pages'),
                    'cost': float(printout_data.get('cost')),
                    'custom_message': printout_data.get('custom_message', ''),
                    'print_on_one_side': printout_data.get('print_on_one_side', True),
                    # 'file': file,
                }

                serializer = ActivePrintoutsSerializer(data=data)

                if serializer.is_valid():
                    serializer.save()
                else:
                    # If any printout fails validation, return the error message immediately
                    return Response({'message': 'Printout Order Creation Failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message': 'Printout Orders Created Successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
'''


class CreatePrintout(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request):
        
        # Get the files array, b&w pages array, and coloured pages array
        files = request.FILES.getlist('files')
        black_and_white_pages = request.data.getlist('pages')
        coloured_pages = request.data.getlist('colouredpages')
        costs = request.data.getlist('costs')
        print_on_one_side_list = request.data.getlist('print_on_one_side_list')
        custom_messages = request.data.getlist('custom_messages')

        try:
            # Perform the iteration for each file
            n = len(files)

            for i in range(n):
                file = files[i]
                black_and_white_page = black_and_white_pages[i]
                coloured_page = coloured_pages[i]
                cost = costs[i]
                print_on_one_side = print_on_one_side_list[i]
                custom_message = custom_messages[i]
                
                data = {
                    'user': request.user.pk,
                    'coloured_pages': coloured_page,
                    'black_and_white_pages': black_and_white_page,
                    'cost': float(cost),
                    'custom_message': custom_message,
                    'print_on_one_side': print_on_one_side,
                    'file': file,
                }

                serializer = ActivePrintoutsSerializer(data=data)

                if serializer.is_valid():
                    serializer.save()
                else:
                    # If any printout fails validation, return the error message immediately
                    return Response({'message': 'Printout Order Creation Failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message': 'Printout Orders Created Successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)


def parse_page_ranges(page_ranges):
    pages_to_check = []

    ranges = page_ranges.split(',')
    for item in ranges:
        if '-' in item:
            start, end = map(int, item.split('-'))
            pages_to_check.extend(range(start, end + 1))
        else:
            pages_to_check.append(int(item))
    
    return pages_to_check        
        
        
# To calculate cost for printouts   
# 2rs for b & w page
# 5rs for b & w page with output on it
# 5rs for coloured page
class CostCalculationView(APIView):
    
    def post(self, request):
        
        # Get the files array, b&w pages array, and coloured pages array
        files = request.FILES.getlist('files')
        pages = request.data.getlist('pages')
        coloured_pages = request.data.getlist('colouredpages')
        
        print(str(files))
        print(str(pages))
        print(str(coloured_pages))

        # initialize the cost to 0
        cost = 0

        try:
            # Perform the iteration for each file
            n = len(files)

            for i in range(n):
                file = files[i]
                page = pages[i]
                coloured_page = coloured_pages[i]

                # Save the file temporarily
                temp_file = default_storage.save('temp_files/' + file.name, ContentFile(file.read()))

                # Full path to the temporarily saved file
                temp_path = default_storage.path(temp_file)
                
                extension = str(temp_path).split('.')[-1] 
                
                # if the file is a pdf
                if (extension.lower() == 'pdf'):

                    black_pages, non_black_pages = check_black_content.check_black_content(pdf_path=temp_path, page_ranges=page)

                    cost += 2.0 * len(non_black_pages)
                    cost += 5.0 * len(black_pages)
                    cost += 10.0 * len(parse_page_ranges(coloured_page))
  
                    # Delete the temporarily saved file
                    default_storage.delete(temp_file)
                    
                # if the file is a word document
                elif (extension.lower() == 'docx'):
                    
                    # Convert word file to images and get word document length as return value
                    doc_length = word_to_images.word_to_images(temp_path)
                    
                    # Convert the images into pdf file and get its path as return value
                    images_to_pdfs.images_to_pdfs(doc_length)
                    
                    # # Then perform exact same operations as those on pdf
                    
                    # for example: if 45 images, then,  ceil(45/10) = ceil(4.5) = 5 pdfs
                    no_of_pdfs = ceil(doc_length/10)
    
                    for i in range(no_of_pdfs):
                        
                        pdf_path =  str(Path(__file__).resolve().parent / 'calculate_cost' / 'word' / 'temp_pdfs' / f'{i}.pdf' )
                        pages_to_check = parse_page_ranges(page)
                        actual_pages_to_check = []
                        # first iteration mein 1 to 10 pages lene hai and subtract 0
                        # second iteration mein 11 to 20 pages lene hai and subtract 10
                        # third iteration mein 21 to 30 pages lene hai and subtract 20
                        # and so on..
                        for each_page in pages_to_check:
                            if (each_page > i*10 and each_page <= (i+1)*10):
                                actual_pages_to_check.append(each_page - i*10)
                              
                        if (len(actual_pages_to_check) !=0 ) : 
                            # Convert the array to a string with elements separated by ','
                            actual_pages_to_check_string = ','.join(map(str, actual_pages_to_check))
                            
                            black_pages, non_black_pages = check_black_content.check_black_content(pdf_path=pdf_path, page_ranges=actual_pages_to_check_string)

                            cost += 2.0 * len(non_black_pages)
                            cost += 5.0 * len(black_pages)
                            cost += 10.0 * len(parse_page_ranges(coloured_page))
                        
                        os.remove(pdf_path)

                    # # Delete the temporarily saved file
                    default_storage.delete(temp_file)
                
                else:
                    default_storage.delete(temp_file)
                    return Response({'error': 'Invalid file type. Only pdf and docx accepted'}, status=status.HTTP_400_BAD_REQUEST)                    

            # If everything goes OK, then return the cost
            return Response({'cost': cost}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
     

from django.http import FileResponse, HttpResponse
import requests

class FirstPageGenerationView(APIView):
    
    # permission_classes = (IsAuthenticated, )
    
    def post(self, request):
        
        try:
            subject_name = request.data.get('subject_name')
            subject_code = request.data.get('subject_code')
            faculty_name = request.data.get('faculty_name')
            student_name = request.data.get('student_name')
            faculty_designation = request.data.get('faculty_designation')
            roll_number = request.data.get('roll_number')
            semester = request.data.get('semester')
            group = request.data.get('group')
            image_path = 'maitlogomain.png'
            
            file_path = firstpage.create_word_file(subject_name=subject_name, subject_code=subject_code,
                                faculty_name=faculty_name, student_name=student_name, faculty_designation=faculty_designation,
                                roll_number=roll_number, semester=semester, group=group, image_path=image_path)  

            pdf_data = convert_docx_to_pdf(file_path)

            # Create a response with PDF content?
            pdf_response = HttpResponse(pdf_data, content_type='application/pdf')
            pdf_response['Content-Disposition'] = 'attachment; filename="converted.pdf"'

            # Delete the temporary files
            os.remove(file_path)    

            return pdf_response
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
from rest_framework.parsers import MultiPartParser
import tempfile
from .img_to_pdf import img_to_pdf
    
class ImageToPdfAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        image_files = request.FILES.getlist('images')
        pics_per_page = int(request.POST.get('pics_per_page', 2))  # Default value is 2 if not provided

        if not image_files:
            return Response({"error": "No images provided"}, status=400)

        try:
            # Create a temporary directory to store the images
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save each image file to the temporary directory
                image_paths = []
                for image_file in image_files:
                    file_path = os.path.join(temp_dir, image_file.name)
                    with open(file_path, 'wb') as f:
                        for chunk in image_file.chunks():
                            f.write(chunk)
                    image_paths.append(file_path)

                # Generate PDF using the ImageToPdfConverter
                converter = img_to_pdf.ImageToPdfConverter(directory=temp_dir, pics_per_page=pics_per_page)
                pdf_content = converter.create_pdf()

                # Return the PDF as a response
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="output.pdf"'
                return response

        except Exception as e:
            return Response({"error": str(e)}, status=500)