import cv2

def list_available_cameras(max_devices=10):
    available_cameras = []
    for index in range(max_devices):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
        else:
            # Optionally, you could break early if you hit a non-existent device
            # break
            pass
    return available_cameras

if __name__ == "__main__":
    cameras = list_available_cameras()
    print(f"Available camera indices: {cameras}")
