from inference_sdk import InferenceHTTPClient
from .constants import ROBOFLOW_API_URL, ROBOFLOW_MODEL_ID, BALL_HIT_MOVEMENT_THRESHOLD, SECONDS_SURROUNDING
from ..settings import ROBOFLOW_API_KEY
from inference import InferencePipeline
from inference.core.interfaces.stream.sinks import render_boxes
import math
import cv2
from moviepy import VideoFileClip
import os

# CLIENT = InferenceHTTPClient(
#     api_url=ROBOFLOW_API_URL,
#     api_key=ROBOFLOW_API_KEY
# )

def infer(file_path):
    predictions = []

    def collect_predictions(prediction, _):
        predictions.append(prediction)
    
    pipeline = InferencePipeline.init(
        model_id=ROBOFLOW_MODEL_ID,
        video_reference=file_path,
        # on_prediction=render_boxes,
        on_prediction=collect_predictions,
        api_key=ROBOFLOW_API_KEY,
    )
    pipeline.start()
    pipeline.join()

    return predictions

def detect_ball_hit(inferences, fps):
    hits = []
    video_size = math.dist([0, 0], [inferences[0]["image"]["width"], inferences[0]["image"]["height"]])
    swing_start_frame = -1
    ball_positions = [[-1, -1]] * len(inferences)
    skip_frames = 0
    swing_started = False

    for inference_index in range(len(inferences)):
        # print(inference)
        if (skip_frames > 0):
            skip_frames -= 1
            continue
        club_y = -1
        club_head_y = -1

        for prediction in inferences[inference_index]["predictions"]:
            if prediction["class"] == "club":
                club_y = prediction["y"]
            elif prediction["class"] == "club_head":
                club_head_y = prediction["y"]
            elif prediction["class"] == "golfball":
                ball_positions[inference_index] = [prediction["x"], prediction["y"]]

        if club_y != -1 and club_head_y != -1:
            if club_head_y < club_y and not swing_started: #club head is above club
                # print("detected club head above club, index:", inference_index)
                swing_started = True
                swing_start_frame = inference_index

        prev_applicable_frame = -1
        min_search_ind = -1
        if (hits):
            min_search_ind = hits[-1][2]
        
        for i in range(inference_index - 1, min_search_ind, -1):
            if (ball_positions[i][0] != -1):
                prev_applicable_frame = i
                break

        # print("current frame:", inference_index, "prev_applicable_frame:", prev_applicable_frame)
        if prev_applicable_frame < swing_start_frame: # The only applicable frame is before the swing started
            continue
        
        # print("we got here. index:", inference_index, "swing_started:", 
        #       swing_started, "ball_position:", ball_positions[inference_index][0], 
        #       "prev_ball_position:", ball_positions[prev_applicable_frame][0])
    
        if (swing_started and
            ball_positions[inference_index][0] != -1 and
            ball_positions[prev_applicable_frame][0] != -1):

            # print("We got here as well")

            # print([ball_positions[prev_applicable_frame][0], ball_positions[prev_applicable_frame][1]], [ball_positions[inference_index][0], ball_positions[inference_index][1]])
            ball_position_change = math.dist([ball_positions[prev_applicable_frame][0], ball_positions[prev_applicable_frame][1]],
                                             [ball_positions[inference_index][0], ball_positions[inference_index][1]])
            
            # print("index:", inference_index, "ball_position_change:", ball_position_change)
            if ball_position_change > video_size * BALL_HIT_MOVEMENT_THRESHOLD * (30 / fps):
                print("hit detected")
                # Ball moved enough to be considered a hit
                hits.append((int(inference_index - fps * SECONDS_SURROUNDING), int(min(len(inferences), inference_index + fps * SECONDS_SURROUNDING))))
                skip_frames = fps * SECONDS_SURROUNDING * 2 # Skip the next 2 seconds of frames
                swing_started = False
    print(hits)
    return(hits)

def get_fps(path):
    cam = cv2.VideoCapture(path)
    return cam.get(cv2.CAP_PROP_FPS)

def clip_video(path: str, start_time: float, end_time: float, index: str, output_dir: str):
    clip = VideoFileClip(path)
    subclip = clip.subclipped(start_time, end_time)

    os.makedirs(output_dir, exist_ok=True)

    subclip.write_videofile(os.path.join(output_dir, str(index) + ".mp4"), codec="libx264")