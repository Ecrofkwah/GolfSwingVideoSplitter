from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from .utils import infer, detect_ball_hit, get_fps, clip_video
import os
import onnxruntime as ort
from ..settings import MEDIA_ROOT
import uuid

# Write a function to that takes a video file and applies another function to it
# Request details: Video file, Frames before, Frames after
# Delete the video file after processing
@api_view(['POST'])
def splitVideoBySwings(request):
    print("Available execution providers:")
    print(ort.get_available_providers())
    #name ,video = next(iter(request.FILES))
    video = request.FILES.get('video')
    # frames_before = request.data['frames_before']
    #frames_after = request.data['frames_after']

    # Save the video file to the server
    video_path = default_storage.save(video.name, video)

    absolute_path = os.path.join(MEDIA_ROOT, video_path)

    unique_id = str(uuid.uuid4())
    output_folder = os.path.join(MEDIA_ROOT, "processed", unique_id)

    extension = os.path.splitext(video.name)[1].lower()

    if extension not in ['.mp4', '.mov', '.avi']:
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Unsupported video format.")
    
    fps = get_fps(absolute_path)
    inference = infer(absolute_path)
    # Call the function that splits the video
    # golfSwingFrames = split_video(video_path, frames_before, frames_after)x

    hits = detect_ball_hit(inference, fps)

    urls = []
    for i in range(len(hits)):
        clip_video(absolute_path, hits[i][0]/fps, hits[i][1]/fps, i, output_folder)
        urls.append(os.path.join(output_folder, str(i) + ".mp4"))

    # Delete the video file
    default_storage.delete(video_path)

    return Response(status=status.HTTP_200_OK, data={"urls": urls, "hits": hits, "FPS": fps})

@api_view(['POST'])
def mirrorResponse(request):
    return Response(status=status.HTTP_200_OK, data=request.FILES.get("vid"))
