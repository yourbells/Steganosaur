from stegano import lsb
from caesarcipher import CaesarCipher
from subprocess import STDOUT
from flask import Blueprint, render_template, current_app, request, flash
from werkzeug.utils import secure_filename
import cv2
import os
import shutil

video = Blueprint("video", __name__, static_folder="static", template_folder="templates")

# Algoritma Caesar Cipher
def caesar_cipher_encrypt(message, shift):
    cipher = CaesarCipher(message=message, encode=True, offset=shift)
    encrypted_message = cipher.encoded
    return encrypted_message

def caesar_cipher_decrypt(message, shift):
    cipher = CaesarCipher(message=message, decode=True, offset=shift)
    decrypted_message = cipher.decoded
    return decrypted_message

# encrypt Video
def encrypt(input_file, input_string, shift, output_file):
    frame_extraction(input_file)
    print(os.getcwd())
    path = str(os.getcwd()) + \
        "\static\\ffmpeg-4.3.1-2020-10-01-full_build\\bin\\ffmpeg"
    print(path)

    encode_string(input_string, shift)
    
    sec_command = path + " -i tmp/%d.png -r 30 -f avi -c:v huffyuv -b:v 2M "+ output_file + " -y"
    # sec_command = path + " -i tmp/%d.png -vcodec png " + output_file + " -y"
    # sec_command = path + " -i tmp/%d.png -vcodec -c:v libx264 -qp 0 " + output_file + " -y"
    print(sec_command)
    os.system(sec_command)  

def frame_extraction(video):
    if not os.path.exists("./tmp"):
        os.makedirs("tmp")
    temp_folder = "./tmp"
    print("[INFO] tmp directory is created")

    vidcap = cv2.VideoCapture(video)
    count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1

def encode_string(input_string, shift, root="./tmp/"):
    ciphertxt = caesar_cipher_encrypt(input_string, shift)
    list_string= [str(x) for x in ciphertxt]
    print(ciphertxt)
    print(type(ciphertxt))
    #convert integer to string list
    #split_string_list = split_string(ciphertxt)
    for i in range(0, len(list_string)):
        f_name = "{}{}.png".format(root, i)
        secret_enc = lsb.hide(f_name, list_string[i])
        secret_enc.save(f_name)
        print("[INFO] frame {} holds {}".format(f_name, list_string[i]))

def decrypt(video, shift):
    frame_extraction(video)
    secret = []
    root = "./tmp/"
    for i in range(len(os.listdir(root))):
        f_name = "{}{}.png".format(root, i)
        secret_dec = lsb.reveal(f_name)
        if secret_dec == None:
            break
        secret.append(secret_dec)
    result = ''.join([i for i in secret])

    final_result = caesar_cipher_decrypt(result, shift)
    print(final_result)
    clean_tmp()
    return final_result

def clean_tmp(path="./tmp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] tmp files are cleaned up")

@video.route("/encode")
def video_encode():
    return render_template("encode.html")

@video.route("/encode-result", methods=['POST', 'GET'])
def video_encode_result():
    if request.method == 'POST':
        message = request.form['message']
        caesar_shift = int(request.form['caesar_shift'])
        if 'file' not in request.files:
            flash('No video found')
            # return redirect(request.url)
        file = request.files['video']
        if file.filename == '':
            flash('No selected video')
            # return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_VIDEO_FOLDER'], filename)
            file.save(file_path)
            encryption = True
            
            output_filename = os.path.splitext(filename)[0] + "_hasil.avi"
            output_file_path = os.path.join(current_app.config['UPLOAD_VIDEO_FOLDER'], output_filename)
            encrypt(file_path, message, caesar_shift, output_file_path)
        else:
            encryption = False
        result = request.form
        return render_template("encode-result.html", message=message, result=result, file=output_filename, encryption=encryption)

@video.route("/decode")
def video_decode():
    return render_template("decode.html")

@video.route("/decode-result", methods=['POST', 'GET'])
def video_decode_result():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No Video found')
            # return redirect(request.url)
        file = request.files['video']
        caesar_shift = int(request.form['caesar_shift'])
        if file.filename == '':
            flash('No selected video')
            # return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_VIDEO_FOLDER'], filename))
            decryption = True
            decrpytedText = decrypt(os.path.join(
                current_app.config['UPLOAD_VIDEO_FOLDER'], filename), caesar_shift)
        else:
            decryption = False
        result = request.form
        return render_template("decode-result.html", result=result, decrypytedText=decrpytedText, file=file, decryption=decryption)
