#!/usr/bin/env python3
# importing the module
import cv2

start = True
fd = open("coordinates.txt", "w")


# function to display the coordinates of
# of the points clicked on the image
def click_event(event, x, y, flags, params):
    global start
    global fd

    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        # displaying the coordinates
        # on the Shell
        print(x, " ", y)
        if start:
            fd.write(f"s = ({x}, {img.shape[0] - y})\ntargets = [\n")
            start = False
        else:
            fd.write(f"    ({x}, {img.shape[0] - y}),\n")
        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.circle(img, (x, y), radius=3, color=(255, 0, 0), thickness=-1)
        # cv2.putText(img, str(x) + ',' +
        # str(y), (x,y), font,
        # 1, (255, 0, 0), 2)
        cv2.imshow("image", img)

    # checking for right mouse clicks
    if event == cv2.EVENT_RBUTTONDOWN:
        # displaying the coordinates
        # on the Shell
        print(x, " ", y)

        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        b = img[y, x, 0]
        g = img[y, x, 1]
        r = img[y, x, 2]
        cv2.putText(
            img, str(b) + "," + str(g) + "," + str(r), (x, y), font, 1, (255, 255, 0), 2
        )
        cv2.imshow("image", img)


# driver function
if __name__ == "__main__":
    # reading the image
    img = cv2.imread("tonopah_rotated.png", 1)
    fd.writelines([f"Dimensions = {img.shape[1]}, {img.shape[0]}\n"])

    # displaying the image
    cv2.imshow("image", img)

    # setting mouse handler for the image
    # and calling the click_event() function
    cv2.setMouseCallback("image", click_event)

    # wait for a key to be pressed to exit
    not_done = True
    while not_done:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            fd.write("]")
            fd.close()
            not_done = False
