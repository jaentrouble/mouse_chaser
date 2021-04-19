import cv2
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', dest='video', help='video path')
parser.add_argument('-f', type=int, dest='frames', help='frames per split')
args = parser.parse_args()

vid_path = args.video
n_split = args.frames

cap = cv2.VideoCapture(vid_path)
n = 0
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
initialized = False
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        if not initialized:
            writer = cv2.VideoWriter(
                f'{n//n_split}.mp4', fourcc, 10, (frame.shape[1],frame.shape[0])
            )
            initialized = True
        writer.write(frame)
        n += 1
        if n%n_split == 0:
            writer.release()
            writer = cv2.VideoWriter(
                f'{n//n_split}.mp4', fourcc, 10, (frame.shape[1],frame.shape[0])
            )
    else:
        break
writer.release()
cap.release()

