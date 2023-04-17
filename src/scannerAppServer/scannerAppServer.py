import sys
from flask import Flask, request, render_template, send_file
from io import BytesIO
from barcode import EAN13
from barcode.writer import ImageWriter

sys.path.append("src/")
from transactions import (
    allocate_device_id,
    send_device_location,
    query_device_information,
)
from digital_signatures import KeyLibrary

app = Flask(__name__)


with open("my_location.txt", "r") as file:
    my_location = file.readlines()[0]
sk = KeyLibrary.load_signing_key("priv_key.pem")
keylib = KeyLibrary()
keylib.load("lib.txt")
markers = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/plot", methods=["GET", "POST"])
def plot():
    input_value = None
    if request.method == "POST":
        input_value = request.form["input_value"]

    try:
        id = int(input_value)
    except:
        id = 0

    success, log, data = query_device_information(id)

    markers = []
    if success:
        for location, timestamp in data:
            print(location)
            found, lat, lon = keylib.get_coordinates(location)
            if found:
                markers.append(
                    {
                        "lat": lat,
                        "lon": lon,
                        "popup": "Item received on the {}".format(
                            timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        ),
                    }
                )
            else:
                # TODO: error handling
                pass

    return render_template("plot.html", markers=markers)


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
    try:
        code, destruct = message.split("=")
        destruct = destruct == "true"
        if code.isnumeric():
            # for some reason the barcode scanner cuts the leading number away if it is a 0
            if len(code) == 12:
                code = "0" + code
            # verify that the checksum of the barcode is correct
            if EAN13(code[:-1]).get_fullcode()[-1] == code[-1]:
                device_id = int(code[:-1])
                success, log = send_device_location(
                    device_id, my_location, sk, destruct
                )
                if success:
                    return "Location {} successfully added for device {}.".format(
                        my_location, device_id
                    )
                return "Error while adding location for device {}: {}.".format(
                    device_id, log
                )
            return "Checksum of barcode incorrect, please scan it again."
        return "Error while scanning, please scan the item again."
    except:
        return "Error while scanning, please scan the item again."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=16123, debug=True)
