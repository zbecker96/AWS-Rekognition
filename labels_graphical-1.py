
from PIL import Image, ImageDraw, ImageFont
import boto3
from pprint import pprint, pformat
from io import BytesIO
from image_helpers import get_image
import csv
# --------------------------------------------------------------------
# DO NOT CHANGE THESE FUNCTIONS


def format_text(text, columns):
    '''
    Returns a copy of text that will not span more than the specified number of columns
    :param text: the text
    :param columns: the maximum number of columns
    :return: the formatted text
    '''
    # format the text to fit the specified columns
    import re
    text = re.sub('[()\']', '', pformat(text, width=columns))
    text = re.sub('\n ', '\n', text)
    return text


def text_rect_size(draw, text, font):
    '''
    Returns the size of the rectangle to be used to
    draw as the background for the text
    :param draw: an ImageDraw.Draw object
    :param text: the text to be displayed
    :param font: the font to be used
    :return: the size of the rectangle to be used to draw as the background for the text
    '''
    (width, height) = draw.multiline_textsize(text, font=font)
    return (width * 1.1, height * 1.3)


def add_text_to_img(img, text, pos=(0, 0), color=(0, 0, 0), bgcolor=(255, 255, 255, 128),
                    columns=60,
                    font=ImageFont.truetype('Impact.ttf', 22)):
    '''
    Creates and returns a copy of the image with the specified text displayed on it
    :param img: the (Pillow) image
    :param text: the text to display
    :param pos: a 2 tuple containing the xpos, and ypos of the text
    :param color: the fill color of the text
    :param bgcolor: the background color of the box behind the text
    :param columns: the max number of columns for the text
    :param font: the font to use
    :return: a copy of the image with the specified text displayed on it
    '''

    # make a blank image for the text, initialized to transparent text color
    txt_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_img)

    # format the text
    text = format_text(text, columns)
    # get the size of the text drawn in the specified font
    (text_width, text_height) = ImageDraw.Draw(img).multiline_textsize(text, font=font)

    # compute positions and box size
    (xpos, ypos) = pos
    rwidth = text_width * 1.1
    rheight = text_height * 1.4
    text_xpos = xpos + (rwidth - text_width) / 2
    text_ypos = ypos + (rheight - text_height) / 2

    # draw the rectangle (slightly larger) than the text
    draw.rectangle([xpos, ypos, xpos + rwidth, ypos + rheight], fill=bgcolor)

    # draw the text on top of the rectangle
    draw.multiline_text((text_xpos, text_ypos), text, font=font, fill=color)

    del draw # clean up the ImageDraw object
    return Image.alpha_composite(img.convert('RGBA'), txt_img)


def get_pillow_img(imgbytes):
    """
    Creates and returns a Pillow image from the given image bytes
    :param imgbytes: the bytes of the image
    """
    return Image.open(BytesIO(imgbytes))


# NOTE: YOU DON'T NEED TO USE THIS (round_conf) FUNCTION,
#       IT IS ONLY USED BY THE DOCTESTS!
def round_conf(conf):
    """
    NOTE: YOU DON'T NEED TO USE THIS FUNCTION, IT
          IS ONLY USED BY THE DOCTESTS!

    Given a dictionary with keys Name and Confidence,
    returns a new dictionary with unchanged Name and the Confidence value rounded
    :param conf: a dictionary with keys Name and Confidence
    :return: a new dictionary with unchanged Name and the Confidence value rounded
    """
    return {'Name': conf['Name'], 'Confidence': round(conf['Confidence'])}


# END DO NOT CHANGE SECTION
# --------------------------------------------------------------------

def get_awsLogin():

    lineC = 0
    secretKey = ''
    accessKey = ''
    with open('accessKeys.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for col in csv_reader:
            if(lineC == 1):
                accessKey += col[0]
                secretKey += col[1]
            lineC += 1

    loginCred = (accessKey,secretKey )

    return loginCred


def get_labels(img, confidence=50):
    """
    Gets the labels from AWS Rekognition for the given image
    :param img: either the image bytes or a string that is the URL or filename for an image
    :param confidence: the confidence level (defaults to 50)

    >>> lbls = get_labels('http://www.idothat.us/images/idothat-img/features/pool-patio-lanai/ft-pool-patio-lanai-2.jpg')
    >>> sorted([round_conf(lbl) for lbl in lbls],  key=lambda d: (d['Confidence'], d['Name']), reverse=True)
    [{'Name': 'Water', 'Confidence': 99}, {'Name': 'Pool', 'Confidence': 99}, {'Name': 'Swimming Pool', 'Confidence': 97}, {'Name': 'Building', 'Confidence': 88}, {'Name': 'Tub', 'Confidence': 81}, {'Name': 'Jacuzzi', 'Confidence': 81}, {'Name': 'Hot Tub', 'Confidence': 81}, {'Name': 'Outdoors', 'Confidence': 79}, {'Name': 'Swimming', 'Confidence': 76}, {'Name': 'Sports', 'Confidence': 76}, {'Name': 'Sport', 'Confidence': 76}, {'Name': 'Urban', 'Confidence': 66}, {'Name': 'Porch', 'Confidence': 65}, {'Name': 'Hotel', 'Confidence': 64}, {'Name': 'Garden', 'Confidence': 60}, {'Name': 'Town', 'Confidence': 56}, {'Name': 'City', 'Confidence': 56}, {'Name': 'Resort', 'Confidence': 55}, {'Name': 'Vase', 'Confidence': 54}, {'Name': 'Tree', 'Confidence': 54}, {'Name': 'Pottery', 'Confidence': 54}, {'Name': 'Potted Plant', 'Confidence': 54}, {'Name': 'Plant', 'Confidence': 54}, {'Name': 'Jar', 'Confidence': 54}]

    >>> lbls = get_labels('http://www.idothat.us/images/idothat-img/features/pool-patio-lanai/ft-pool-patio-lanai-2.jpg', 90)
    >>> sorted([round_conf(lbl) for lbl in lbls], key=lambda d: (d['Confidence'], d['Name']), reverse=True)
    [{'Name': 'Water', 'Confidence': 99}, {'Name': 'Pool', 'Confidence': 99}, {'Name': 'Swimming Pool', 'Confidence': 97}]
    """
    # replace pass below with your implementation

    loginCred = get_awsLogin()

    client = boto3.client('rekognition', aws_access_key_id= loginCred[0],
                          aws_secret_access_key= loginCred[1])

    # imgurl = 'http://www.idothat.us/images/idothat-img/features/pool-patio-lanai/ft-pool-patio-lanai-2.jpg'
    #img = 'http://s1.favim.com/orig/18/beach-birds-cute-nature-parrots-Favim.com-194539.jpg'
    # imgurl = 'https://www.parrots.org/images/uploads/dreamstime_C_47716185.jpg'

    imgbytes = get_image(img)  #get the image bytes

    rekresp = client.detect_labels(Image={'Bytes': imgbytes})  #use a rekognition client to detect the labels

    cleanedList = [{'Name': inf['Name'], 'Confidence': inf['Confidence']} for inf in rekresp['Labels'] if inf['Confidence'] >= confidence]  #filter by a confidence val

    cleanedList2 = [inf['Name'] for inf in cleanedList] #trim down to just a list of names

    #return the list of names
    return cleanedList2


def label_image(img, confidence=50):
    '''
    Creates and returns a copy of the image, with labels from Rekognition displayed on it
    :param img: a string that is either the URL or filename for the image
    :param confidence: the confidence level (defaults to 50)

    :return: a copy of the image, with labels from Rekognition displayed on it
    '''
    # replace pass below with your implementation

    labelList = get_labels(img,confidence) #get the labels for a given confidence
    labelListStr = ' , '.join(labelList) #join the list with a comma after each value


    #convert the image to a pillow image
    imgbytes = get_image(img)
    img = get_pillow_img(imgbytes)

    #create a new image with the text added
    img2ElectricBogaloo = add_text_to_img(img, labelListStr,
                       font=ImageFont.truetype('Impact.ttf', 28),
                       bgcolor=(255, 255, 255, 100))


    return img2ElectricBogaloo



if __name__ == "__main__":
    # can't use input since PyCharm's console causes problems entering URLs
    # img = input('Enter either a URL or filename for an image: ')
    #img = 'https://blog.njsnet.co/content/images/2017/02/trumprecognition.png'
    img = 'https://www.parrots.org/images/uploads/dreamstime_C_47716185.jpg'
    labelled_image = label_image(img)
    labelled_image.show()
