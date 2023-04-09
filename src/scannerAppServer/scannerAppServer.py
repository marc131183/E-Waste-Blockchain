import sys
from flask import Flask, request, render_template, send_file
from io import BytesIO
from barcode import EAN13
from barcode.writer import ImageWriter

sys.path.append("src/")
from transactions import allocate_device_id, send_device_location
from digital_signatures import KeyLibrary


app = Flask(__name__)
with open("my_location.txt", "r") as file:
    my_location = file.readlines()[0]
sk = KeyLibrary.load_signing_key("priv_key.pem")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate_barcode")
def generate_barcode():
    success, device_id = allocate_device_id(my_location)
    while not success:
        success, device_id = allocate_device_id(my_location)

    device_id = str(device_id)
    device_id = "0" * (12 - len(device_id)) + device_id
    barcode = EAN13(device_id, writer=ImageWriter())
    buffer = BytesIO()
    barcode.write(buffer)
    barcode_data = buffer.getvalue()
    return send_file(
        BytesIO(barcode_data), download_name="barcode.png", mimetype="image/png"
    )


@app.route("/message", methods=["POST"])
def receive_message():
    message: str = request.json.get("message")
    if message.isnumeric():
        # for some reason the barcode scanner cuts the leading number away if it is 0
        if len(message) == 12:
            message = "0" + message
        # verify that the checksum of the barcode is correct
        if EAN13(message[:-1]).get_fullcode()[-1] == message[-1]:
            device_id = int(message[:-1])
            success, log = send_device_location(device_id, my_location, sk)
            if success:
                return "Location {} successfully added for device {}.".format(
                    my_location, device_id
                )
            return "Error while adding location for device {}: {}.".format(
                device_id, log
            )
        return "Checksum of barcode incorrect, please scan it again."
    return "Error while scanning, please scan the item again.".format(message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=16123, debug=True)
